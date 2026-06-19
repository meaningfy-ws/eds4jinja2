<!-- The EPIC — the shaped bet. In Meaningfy the EPIC *is* the OpenSpec proposal. -->

# EPIC: Built-in graph store — load RDF files into memory and report on them

## Appetite

**Small.** One new adapter module (a port + two engine adapters + a factory), one builder
registration, one opt-in optional extra in `pyproject.toml`, parity-inheriting tests, a minor
version bump. No template changes, no public-API removals, no new *mandatory* dependency, no CLI
changes.

## Why

The sibling change `in-memory-sparql-datasource` gives `eds4jinja2` an engine-agnostic
`InMemorySPARQLDataSource` that renders reports against a graph **the consumer already holds** —
the consumer still owns graph loading. That leaves the most common case unserved: *"I have RDF
files (or URLs) and I just want a report — no SPARQL server, and no loading code I have to write
myself."*

Today the only file-path source is `RDFFileDataSource` (`adapters/local_sparql_ds.py`), and it
has three baked-in limits: it takes a **file path only** (no URLs, no handed-in graph), it
**re-parses the file on every `_fetch_tabular`** (`self.__graph__.parse(self.__filename__)` runs
per query), and it is **tabular-only** (`_fetch_tree` raises `UnsupportedRepresentation`). We
need eds4jinja2 ITSELF to load one-or-more RDF sources into an in-memory graph **once**, with a
choice of engine (rdflib or oxigraph), and query it through the already-built in-memory adapter —
getting both tabular and tree shapes for free.

This change is the thin loading layer that sits **on top of** the sibling change.

## Solution outline

One additive move, layered on the sibling adapter:

1. **A graph-store port and two engine adapters** in `adapters/graph_store.py`:
   - `Engine(str, Enum)` with `RDFLIB = "rdflib"` and `OXIGRAPH = "oxigraph"` — no free strings;
     a template-supplied engine string is converted at the boundary via `Engine(value)`.
   - `GraphStorePort(ABC)` with `load(self, source: str) -> None` and a `query` capability whose
     result is directly consumable by `InMemorySPARQLDataSource`'s existing normaliser (rdflib
     `Result`, or pyoxigraph `QuerySolutions` / `QueryTriples`).
   - `RdflibGraphStore` — wraps a fresh or handed-in `rdflib.Graph`; `load` = `graph.parse(source)`
     (handles file paths AND URLs natively); `query` = `graph.query`.
   - `OxigraphGraphStore` — wraps a fresh or handed-in `pyoxigraph.Store`; `load` uses
     `store.load(...)` for files and fetch-bytes-then-load (via the already-present `requests`
     dependency) for URLs; `query` = `store.query`. **`pyoxigraph` is imported lazily inside the
     class — never at module top.**
   - `make_graph_store(engine, sources=None, graph=None) -> GraphStorePort` — the factory that
     **loads each source exactly once at construction** (the explicit fix for the re-parse smell).

2. **A `from_rdf` builder** registered in `DATA_SOURCE_BUILDERS` (`builders/jinja_builder.py`):
   ```python
   "from_rdf": lambda sources, engine="rdflib":
       InMemorySPARQLDataSource(make_graph_store(Engine(engine), sources=sources).query),
   ```
   `sources` accepts a single path/URL or a list. Default engine is **rdflib** (zero new deps for
   the default path). `from_rdf` just builds a store, loads once, and wraps `store.query` — no new
   result-mapping code; the tabular/tree shapes are inherited from the sibling adapter.

**Scenario 1 (the bet):** a template author writes `{{ from_rdf("dataset.ttl") }}` (or
`from_rdf(["a.ttl", "https://example/b.ttl"], engine="oxigraph")`) and renders a full report
straight from RDF files — no SPARQL server, no consumer-written loading code.

`from_rdf` **supersedes** the legacy `from_rdf_file` (file-path-only, re-parse-per-query,
tabular-only) **without removing or changing it**.

## Key decisions

- **DEC-1 (build on the sibling adapter)**: `from_rdf` is built on `InMemorySPARQLDataSource`
  from the sibling `in-memory-sparql-datasource` change (golden-thread dependency). It only
  builds a store, loads sources once, and wraps `store.query`. **No new result-mapping / tree /
  tabular code** is written here — the shapes are inherited. *(Why: parity for free; one
  normaliser to maintain.)*
- **DEC-2 (engine via enum, rdflib default)**: the engine is selected through the `Engine` enum;
  **rdflib is the default**. rdflib is already a dependency (`local_sparql_ds.py`), so the
  default path adds **zero new dependencies** and stays pyoxigraph-free.
- **DEC-3 (oxigraph is an opt-in extra; reconciliation with the sibling no-go)**: oxigraph
  support is OPT-IN. Add `oxigraph = ["pyoxigraph~=0.4"]` to `[project.optional-dependencies]`;
  `pyoxigraph` is **lazily imported only inside `OxigraphGraphStore`**, never at module top. This
  change **deliberately and narrowly relaxes** the sibling change's *"no pyoxigraph import,
  ever"* no-go — but ONLY as an opt-in extra: the rdflib path and the library core stay
  pyoxigraph-free, and pyoxigraph never becomes a mandatory dependency. *(We state this
  reconciliation explicitly so the two changes' no-gos do not appear to contradict.)*
- **DEC-4 (load once)**: the graph is parsed **once at store construction** and reused across
  every query — the explicit fix for `RDFFileDataSource`'s per-query re-parse.
- **DEC-5 (naming — two complementary builders)**: `from_rdf(sources, engine)` means *"we load
  files/URLs into memory for you"*; the sibling change's `from_memory` (alias `from_store`) means
  *"bring your own in-memory graph"*. They are distinct, complementary builders — neither
  replaces the other.
- **DEC-6 (result-shape parity inherited)**: tabular `DataFrame` and tree SPARQL-JSON shapes are
  inherited from `InMemorySPARQLDataSource` — both shapes supported for **both** engines, with no
  shape code in this change.
- **DEC-7 (forward-compatible concurrent reads)**: graph stores MUST be safe for concurrent
  **read** queries (a future `parallel-report-executor` change will pre-warm fetches across
  threads). **No write concurrency** — the store is read-only after loading.
- **DEC-8 (versioning)**: a **MINOR** bump (additive, non-breaking). The exact number depends on
  ship order relative to the in-memory core; state **"next MINOR"** rather than a hard number.

## Rabbit-holes

- Do **not** re-implement a SPARQL engine. Querying is delegated to `graph.query` (rdflib) or
  `store.query` (pyoxigraph); the loading layer only parses sources and hands the `query`
  callable to the sibling adapter.
- Do **not** import `pyoxigraph` at module top or anywhere on the rdflib path — the lazy import
  lives strictly inside `OxigraphGraphStore`.
- Do **not** re-derive tabular/tree shapes — they come from `InMemorySPARQLDataSource`. Writing
  new mapping code here would duplicate (and risk drifting from) the sibling normaliser.
- Avoid over-modelling sources. A source is a path-or-URL string (or a list of them); the factory
  iterates and loads each once. Nothing more.
- Do not chase serialization-format parity between rdflib and pyoxigraph for exotic typed literals
  in the first pass (see Open Questions in design.md).

## No-gos

<!-- MANDATORY. Explicitly out of scope. -->

- **No reimplementing a SPARQL engine.** Querying is delegated to rdflib / pyoxigraph.
- **No mandatory `pyoxigraph` dependency.** It is an opt-in extra, lazily imported; the default
  (rdflib) path and the core stay pyoxigraph-free.
- **No removal or behaviour change** of `from_rdf_file`, `RDFFileDataSource`, or any existing
  data source. `from_rdf` is additive.
- **rdflib stays the default engine.** oxigraph is never the default.
- **No write / update operations** on the graph — read-only querying after loading.
- **No `mkreport` CLI changes** in this change.
- **No template changes** to existing dqgen-style templates; `from_rdf` is a new opt-in call.

---

## What Changes

- Add `eds4jinja2/adapters/graph_store.py` with `Engine(str, Enum)`, `GraphStorePort(ABC)`,
  `RdflibGraphStore`, `OxigraphGraphStore` (lazy `pyoxigraph` import), and the
  `make_graph_store(engine, sources=None, graph=None)` factory that loads each source **once**.
- Register `from_rdf` in `DATA_SOURCE_BUILDERS` (`builders/jinja_builder.py`) as
  `lambda sources, engine="rdflib": InMemorySPARQLDataSource(make_graph_store(Engine(engine),
  sources=sources).query)`; `sources` accepts a single path/URL or a list; default engine rdflib.
- Add `oxigraph = ["pyoxigraph~=0.4"]` to `[project.optional-dependencies]` in `pyproject.toml`.
- Add unit tests for the graph store (load-once; rdflib + oxigraph engines; single + multiple
  sources; missing/unknown engine errors; concurrent-read safety) and for the `from_rdf` builder
  (tabular + tree parity inherited from `InMemorySPARQLDataSource`).
- Bump `__version__` to the next MINOR and add a changelog/README note. **MINOR, non-breaking.**

## Capabilities

### New Capabilities
- `builtin-graph-store`: eds4jinja2 loads one-or-more RDF files/URLs into an in-memory graph
  (engine configurable — rdflib default, oxigraph opt-in), loaded **once**, and queries it via
  the in-memory adapter — rendering reports directly from RDF files with no SPARQL server and no
  consumer-written loading code, with tabular + tree parity.

### Modified Capabilities
<!-- None: no existing spec carries requirements for these areas yet. The legacy
     `from_rdf_file` / `RDFFileDataSource` is superseded but untouched. -->

## Impact

- **Code**: new `eds4jinja2/adapters/graph_store.py`; `eds4jinja2/builders/jinja_builder.py`
  (register `from_rdf`); new tests under `tests/unit/`.
- **APIs**: new public `Engine`, `GraphStorePort`, `RdflibGraphStore`, `OxigraphGraphStore`,
  `make_graph_store`; new `from_rdf` template builder. All additive.
- **Dependencies**: `pyproject.toml` gains an **opt-in** `oxigraph` extra (`pyoxigraph~=0.4`);
  the default path adds nothing (rdflib already present; `requests` already present for URL
  fetching on the oxigraph path).
- **Version**: 0.3.1 → next MINOR (additive, non-breaking).
- **Golden thread / driver**: layered ON TOP OF the sibling `in-memory-sparql-datasource` change
  (depends on its `InMemorySPARQLDataSource`); forward-compatible with a future
  `parallel-report-executor` change (concurrent-read safety, DEC-7).
