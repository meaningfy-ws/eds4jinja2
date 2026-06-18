<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Parent: EPIC `builtin-graph-store` (proposal.md) — derived from DEC-1..DEC-8.

## Context

`eds4jinja2` drives Jinja2 report templates from pluggable data sources. Templates call builder
lambdas registered in `DATA_SOURCE_BUILDERS` (`builders/jinja_builder.py`):

```python
DATA_SOURCE_BUILDERS = {
    "from_endpoint": lambda endpoint: RemoteSPARQLEndpointDataSource(endpoint),
    "from_file":     lambda file_path: FileDataSource(file_path),
    "from_rdf_file": lambda from_rdf_file: RDFFileDataSource(from_rdf_file),
}
```

The sibling change `in-memory-sparql-datasource` adds `InMemorySPARQLDataSource(DataSource)`,
which accepts **either** an `rdflib.Graph` **or** a `query(sparql_text) -> results` callable, and
implements **both** `_fetch_tabular` (a pandas `DataFrame` of stringified bindings) and
`_fetch_tree` (the SPARQL 1.1 JSON results object). Its normaliser already consumes rdflib
`Result` objects and pyoxigraph-style solutions. **That adapter is the foundation this change
builds on.**

The gap this change closes is *loading*: the only file-path source today,
`RDFFileDataSource` (`adapters/local_sparql_ds.py`), is:

- **file-path only** — `__init__(self, filename)`, no URL and no handed-in graph;
- **re-parsing per query** — `_fetch_tabular` runs `self.__graph__.parse(self.__filename__)` on
  every call (the smell);
- **tabular-only** — `_fetch_tree` raises `UnsupportedRepresentation`.

The `DataSource` ABC (`adapters/base_data_source.py`) provides the fail-safe wrappers
(`fetch_tabular` / `fetch_tree` returning `(result, error)` and catching every `Exception`), so a
load failure raised inside the store propagates through `_fetch_*` and is converted to
`(None, error)` with no new error plumbing.

**Constraints**: layers `entrypoints > builders > adapters` (adapters innermost — import-linter
enforced; `graph_store.py` imports nothing upward); Python 3.11/3.12; pip + tox + pyproject;
rdflib and `requests` already dependencies; `pyoxigraph` is NOT a dependency and may be added only
as an opt-in extra, lazily imported.

## Goals / Non-Goals

**Goals:**
- Render reports directly from one-or-more RDF files/URLs with **no SPARQL server and no
  consumer-written loading code** (Scenario 1).
- Load each source **exactly once** at store construction, reused across queries (fix the
  `RDFFileDataSource` re-parse smell).
- Make the engine configurable (rdflib default, oxigraph opt-in) behind a single `Engine` enum.
- Inherit tabular + tree parity from `InMemorySPARQLDataSource` (no new shape code).
- Keep `pyoxigraph` out of the default path and out of the core; never make it mandatory.
- Be fully backward-compatible (additive builder; `from_rdf_file` untouched).

**Non-Goals:**
- No SPARQL engine implementation; no query optimisation.
- No removal or behaviour change of `from_rdf_file` / `RDFFileDataSource` / other sources.
- No write/update on the graph (read-only after load).
- No CLI changes; no changes to existing templates.
- No new result-shape code (inherited from the sibling adapter).

## Decisions

- **DEC-1 (build on the sibling adapter)**: `from_rdf` wraps `make_graph_store(...).query` in
  `InMemorySPARQLDataSource`. No tabular/tree mapping here. *(Alternatives: a bespoke file→tree
  source — rejected, duplicates the sibling normaliser and risks shape drift.)*
- **DEC-2 (engine enum, rdflib default)**: `class Engine(str, Enum): RDFLIB = "rdflib";
  OXIGRAPH = "oxigraph"`. A template-supplied engine string is converted at the boundary with
  `Engine(value)` (so an unknown string raises `ValueError` — no free strings, fail fast).
  `from_rdf`'s default is `"rdflib"`. *(Why: subclassing `str` lets `Engine.RDFLIB == "rdflib"`
  and keeps template ergonomics while banishing magic strings.)*
- **DEC-3 (port + two adapters)**: `GraphStorePort(ABC)` declares `load(self, source: str) -> None`
  and `query(self, sparql: str)`. `RdflibGraphStore` and `OxigraphGraphStore` implement it. The
  port keeps `make_graph_store` and `from_rdf` engine-blind (DIP). *(Alternatives: a single class
  branching on engine internally — rejected, violates OCP; adding a third engine would pile up
  conditionals.)*
- **DEC-4 (lazy pyoxigraph)**: `import pyoxigraph` happens **inside** `OxigraphGraphStore`
  methods/`__init__`, never at module top. If the extra is not installed, the `ImportError` is
  caught and re-raised as an actionable message (`install eds4jinja2[oxigraph]`). *(Why: keeps the
  module importable and the rdflib path pyoxigraph-free.)*
- **DEC-5 (load once)**: `make_graph_store(engine, sources=None, graph=None)` constructs the store
  and calls `store.load(source)` for each source **once**, then returns the store. Queries reuse
  the already-parsed graph. *(Why: the explicit fix for the re-parse smell.)*
- **DEC-6 (URL handling per engine)**: rdflib `graph.parse(source)` resolves both file paths and
  URLs natively. pyoxigraph `Store.load` reads files but has no HTTP fetch, so
  `OxigraphGraphStore.load` detects a URL (scheme `http`/`https`), fetches bytes with the
  already-present `requests`, and loads the bytes. *(Why: URL parity across engines without a new
  dependency.)*
- **DEC-7 (read-only, concurrent-read-safe)**: stores expose only `load` (construction-time) and
  `query` (read). After loading, concurrent `query` calls must be safe. No write API. *(Why:
  forward-compat with `parallel-report-executor`; both rdflib `Graph.query` and pyoxigraph
  `Store.query` are read-safe against a quiescent store.)*

## Algorithm / approach

**A. graph_store.py** (`adapters/graph_store.py`):

```python
from abc import ABC, abstractmethod
from enum import Enum
from urllib.parse import urlparse

import rdflib
import requests


class Engine(str, Enum):
    RDFLIB = "rdflib"
    OXIGRAPH = "oxigraph"


def _is_url(source: str) -> bool:
    return urlparse(str(source)).scheme in ("http", "https")


class GraphStorePort(ABC):
    """A loadable, queryable in-memory RDF graph. Read-only after loading."""

    @abstractmethod
    def load(self, source: str) -> None:
        """Parse one RDF source (file path or URL) into the in-memory graph."""

    @abstractmethod
    def query(self, sparql: str):
        """Evaluate a SPARQL query; result is consumable by InMemorySPARQLDataSource."""


class RdflibGraphStore(GraphStorePort):
    def __init__(self, graph: "rdflib.Graph | None" = None):
        self._graph = graph if graph is not None else rdflib.Graph()

    def load(self, source: str) -> None:
        self._graph.parse(source)          # handles file paths AND URLs natively

    def query(self, sparql: str):
        return self._graph.query(sparql)   # rdflib Result -> sibling normaliser


class OxigraphGraphStore(GraphStorePort):
    def __init__(self, store=None):
        pyoxigraph = self._import_pyoxigraph()
        self._store = store if store is not None else pyoxigraph.Store()

    @staticmethod
    def _import_pyoxigraph():
        try:
            import pyoxigraph                       # lazy: never at module top
            return pyoxigraph
        except ImportError as exc:                  # actionable message
            raise ImportError(
                "The oxigraph engine requires pyoxigraph. Install it with "
                "`pip install eds4jinja2[oxigraph]`."
            ) from exc

    def load(self, source: str) -> None:
        pyoxigraph = self._import_pyoxigraph()
        if _is_url(source):
            response = requests.get(source)         # requests already a dependency
            response.raise_for_status()
            self._store.load(response.content, ...)  # bytes -> store
        else:
            self._store.load(path=source, ...)       # file path -> store

    def query(self, sparql: str):
        return self._store.query(sparql)             # QuerySolutions / QueryTriples


_STORE_BY_ENGINE = {
    Engine.RDFLIB: RdflibGraphStore,
    Engine.OXIGRAPH: OxigraphGraphStore,
}


def make_graph_store(engine: Engine, sources=None, graph=None) -> GraphStorePort:
    """Build a store for `engine` and load each source EXACTLY ONCE (DEC-5)."""
    engine = Engine(engine)                          # ValueError on unknown string
    store = (RdflibGraphStore(graph=graph) if engine is Engine.RDFLIB
             else _STORE_BY_ENGINE[engine]())
    for source in _normalise_sources(sources):       # str -> [str]; list passes through
        store.load(source)
    return store
```

**B. from_rdf builder** (`builders/jinja_builder.py`):

```python
from eds4jinja2.adapters.graph_store import Engine, make_graph_store
from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource   # sibling change

DATA_SOURCE_BUILDERS = {
    "from_endpoint": lambda endpoint: RemoteSPARQLEndpointDataSource(endpoint),
    "from_file":     lambda file_path: FileDataSource(file_path),
    "from_rdf_file": lambda from_rdf_file: RDFFileDataSource(from_rdf_file),   # legacy, untouched
    "from_rdf":      lambda sources, engine="rdflib":
        InMemorySPARQLDataSource(make_graph_store(Engine(engine), sources=sources).query),
}
```

**Worked example (template — Scenario 1):**

```jinja
{% set data = from_rdf("dataset.ttl").with_query(my_select) %}        {# rdflib default #}
{% set big  = from_rdf(["a.ttl", "https://example/b.ttl"], engine="oxigraph")
                .with_query(my_select) %}                              {# oxigraph, multi-source #}
```

No SPARQL server, no consumer-written loading code. The store parses each source once at
construction; `with_query(...)` / `_fetch_tabular` / `_fetch_tree` are inherited from
`InMemorySPARQLDataSource`, so tabular DataFrame and tree SPARQL-JSON both work for both engines.

### Anti-patterns
- ❌ Importing `pyoxigraph` at module top or on the rdflib path (lazy import lives only inside
  `OxigraphGraphStore`).
- ❌ Re-parsing a source per query (the `RDFFileDataSource` smell — load once in
  `make_graph_store`).
- ❌ Writing new tabular/tree mapping code here (inherit it from `InMemorySPARQLDataSource`).
- ❌ Branching on a raw engine string with `if engine == "oxigraph"` — use the `Engine` enum and a
  dispatch map; no free strings.
- ❌ A single store class that switches engines internally (OCP smell — use the port + adapters).
- ❌ Exposing any write/update API on the store (read-only after loading).
- ❌ Swallowing the missing-pyoxigraph `ImportError` silently — re-raise it with the
  `eds4jinja2[oxigraph]` install hint.

## Error matrix

| Failure mode | Expected handling |
|---|---|
| `engine="oxigraph"` but `pyoxigraph` not installed | `OxigraphGraphStore` re-raises `ImportError` with an actionable message ("install `eds4jinja2[oxigraph]`"); surfaces at store construction |
| Unknown engine string (e.g. `"jena"`) | `Engine(value)` raises `ValueError` at the boundary (fail fast, before any load) |
| Source file missing / unparseable | the engine's `load` raises; propagates through `_fetch_*` and the `DataSource` fail-safe wrapper returns `(None, error)` |
| URL fetch fails on the oxigraph path | `requests` raises (`raise_for_status` / connection error); propagates the same fail-safe way |
| Empty `sources` (`None` / `[]`) | an empty graph is built; queries return empty results (empty DataFrame / empty bindings) — no crash |
| `with_query` never called / empty query | inherited from `InMemorySPARQLDataSource`: `_fetch_*` raises `"The query is empty."`; wrapper returns `(None, error)` |
| Concurrent read queries | safe — store is quiescent after loading; no write API (DEC-7) |

## Risks / Trade-offs

- **[pyoxigraph becoming a hidden hard dependency]** → Mitigation: lazy import strictly inside
  `OxigraphGraphStore`; a test imports `graph_store` and constructs the rdflib path with
  `pyoxigraph` absent (monkeypatched) and asserts no import error.
- **[Re-parse smell sneaking back]** → Mitigation: a test patches the engine `load` and asserts it
  is called exactly once per source across two queries against the same `from_rdf(...)` source.
- **[Result-shape drift vs the sibling adapter]** → Mitigation: parity is inherited, not
  re-derived; tests assert tabular `DataFrame` and tree `head.vars`/`results.bindings` for both
  engines through the same `InMemorySPARQLDataSource`.
- **[Serialization-format parity rdflib vs pyoxigraph]** → Mitigation: first pass covers Turtle
  (and the format the loader infers); typed-literal canonicalisation differences parked (Open
  Questions).
- **[oxigraph version churn]** → Mitigation: pin `pyoxigraph~=0.4`; the lazy import isolates the
  blast radius to the opt-in path.

## Open Questions

- **oxigraph version pin**: `pyoxigraph~=0.4` is the first-pass pin; confirm against the consumer's
  installed major and revisit if the consumer needs a newer line. *(Parked: opt-in path only.)*
- **Serialization-format parity for tree term-typing** between rdflib and pyoxigraph (datatype IRI
  vs prefixed form, blank-node labelling). First pass relies on the sibling normaliser's existing
  behaviour; revisit if a consumer needs canonical typing across engines. *(Parked: low risk for
  dqgen tabular-first templates.)*
- Whether `from_rdf` should accept an explicit `format=` hint for ambiguous extensions, or keep
  relying on engine content-type/extension sniffing. *(Defaulting to sniffing; reconsider on a
  concrete miss.)*
