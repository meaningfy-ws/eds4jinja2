<!-- The EPIC — the shaped bet. In Meaningfy the EPIC *is* the OpenSpec proposal. -->

# EPIC: In-memory SPARQL data source for server-less reporting

## Appetite

**Small.** One new adapter, one constructor seam, parity tests, a minor version bump.
No template changes, no public-API removals, no new hard dependency.

## Why

`eds4jinja2` can only feed reports from data sources that exist *outside* the process: a
remote SPARQL endpoint (`RemoteSPARQLEndpointDataSource`, needs a running server) or a file
path (`RDFFileDataSource`, re-parses the file on every query and supports tabular only — its
`_fetch_tree` raises `UnsupportedRepresentation`). A consumer that already holds an RDF graph
in memory (e.g. an `rdflib.Graph`, or a pyoxigraph-backed store) has **no way** to render a
report against it without standing up a Fuseki/SPARQL server. Worse, even if it could, the
`ReportBuilder` constructor is hardwired to the default data-source builders — it calls
`build_eds_environment(loader=…, **syntax)` with **no** hook to inject alternative builders,
so the in-template `from_endpoint(conf.default_endpoint)` call cannot be redirected. We need
in-memory reporting **with the dqgen-style templates left untouched**, and that requires
exactly two things: a builder-injection seam on `ReportBuilder`, and an in-memory `DataSource`.

## Solution outline

Two small, additive moves, both backward-compatible:

1. **Builder-injection seam.** Add two optional, empty-default keyword arguments to
   `ReportBuilder.__init__` — `external_data_source_builders: dict = {}` and
   `external_filters: dict = {}` — and forward them into the existing
   `build_eds_environment(...)` call (which already accepts both parameters). Empty defaults
   reproduce today's behaviour byte-for-byte. This is the key unlock: a consumer can now
   override the `from_endpoint` builder the templates already call.

2. **`InMemorySPARQLDataSource(DataSource)`.** A new adapter that wraps an engine-agnostic
   source — accepting **either** an `rdflib.Graph` **or** a `query(sparql_text) -> results`
   callable — and implements **both** `_fetch_tabular` (pandas `DataFrame`, same shape as
   `RemoteSPARQLEndpointDataSource`) **and** `_fetch_tree` (SPARQL-JSON `dict`, same shape),
   explicitly closing the tree gap that `RDFFileDataSource` leaves open.

The **consumer pattern** (documented, not enforced): keep templates untouched — they still
call `from_endpoint(conf.default_endpoint)` — and pass
`external_data_source_builders={"from_endpoint": lambda _endpoint: InMemorySPARQLDataSource(store)}`.
Optionally we also register a `from_graph` builder (alias `from_memory`) in `DATA_SOURCE_BUILDERS`
for consumers who prefer to call it explicitly from a template; it takes the in-memory
graph/store (or `query` callable) the consumer already holds.

> **Related additive changes (layered on this core, no conflict):** `builtin-graph-store` adds a
> `from_rdf(sources, engine)` builder that *loads* RDF files/URLs into an in-memory rdflib/oxigraph
> graph (opt-in `pyoxigraph` extra) and reuses `InMemorySPARQLDataSource`; `parallel-report-executor`
> adds opt-in multi-threaded pre-warm of fetches. Both build on this change; neither alters it. The
> "no pyoxigraph, ever" no-go below is scoped to *this* change — `builtin-graph-store` relaxes it as
> an opt-in extra only.

## Key decisions

- **DEC-1**: Inject builders via two optional empty-dict kwargs on `ReportBuilder.__init__`,
  forwarded to `build_eds_environment` — chosen over subclassing or a new builder class
  because `build_eds_environment` already takes `external_data_source_builders` /
  `external_filters`; the only missing link is the `ReportBuilder` constructor. Smallest seam,
  zero behaviour change at the default.
- **DEC-2**: The new data source is **engine-agnostic** — it accepts an `rdflib.Graph` *or* a
  `query(sparql_text)` callable — so it serves both rdflib and pyoxigraph-backed consumers
  without `eds4jinja2` depending on pyoxigraph. `rdflib` is already a dependency
  (`local_sparql_ds.py`); pyoxigraph is reached only through the callable, never imported.
- **DEC-3**: Result shapes **mirror `RemoteSPARQLEndpointDataSource` exactly** — tabular is a
  `DataFrame` of stringified bindings; tree is the SPARQL 1.1 JSON results object
  (`{"head": {...}, "results": {"bindings": [...]}}`). Parity is the contract: templates must
  not be able to tell which source produced the data.
- **DEC-4**: Templates are **frozen**. The unlock is the `from_endpoint` override at build
  time, not a template edit. This keeps every existing dqgen template working unchanged.
- **DEC-5**: **MINOR** version bump (0.3.1 → 0.4.0) with a changelog note. Purely additive;
  no breaking change.

## Rabbit-holes

- Do **not** try to re-implement a SPARQL engine. Tabular comes from `graph.query(...)`
  bindings (or the callable's result); tree is assembled from the same bindings into the
  SPARQL-JSON shape — no custom query planning.
- Do **not** reuse the `RemoteSPARQLEndpointDataSource` `SPARQLClientPool` singleton — the
  in-memory source has no connection to pool.
- Avoid over-modelling the callable contract. It takes a SPARQL string and returns a result
  iterable/object the adapter can normalise; nothing more.
- Do not chase full SPARQL-JSON fidelity for exotic term types in the first pass (see Open
  Questions in design.md) — cover URIs, literals (with datatype/lang), and blank nodes.

## No-gos

<!-- MANDATORY. Explicitly out of scope. -->

- **No template changes.** dqgen-style templates stay byte-for-byte unchanged.
- **No breaking changes** to any existing public signature, default behaviour, or data-source
  contract. Empty-default kwargs only.
- **No new mandatory dependency.** No `pyoxigraph` import in `eds4jinja2`; rdflib is already
  present.
- **No persistence / no I/O.** This source does not read files or open sockets — the consumer
  owns graph loading.
- **No changes to the `mkreport` CLI** in this change.
- **No removal or behaviour change** of `RDFFileDataSource` or `RemoteSPARQLEndpointDataSource`.

---

## What Changes

- Add `external_data_source_builders: dict = {}` and `external_filters: dict = {}` to
  `ReportBuilder.__init__` (`builders/report_builder.py`) and forward them into
  `build_eds_environment(...)`. Empty defaults → identical current behaviour.
- Add `InMemorySPARQLDataSource(DataSource)` in `adapters/in_memory_sparql_ds.py` implementing
  `_fetch_tabular` (DataFrame) and `_fetch_tree` (SPARQL-JSON dict), accepting an
  `rdflib.Graph` or a `query(sparql_text)` callable.
- Register an optional `from_graph` builder (alias `from_memory`) in `DATA_SOURCE_BUILDERS`
  (`builders/jinja_builder.py`) for explicit in-template use.
- Add unit tests for the new adapter (tabular + tree; rdflib.Graph and callable inputs) and
  for `ReportBuilder` builder injection (override `from_endpoint`).
- Bump version 0.3.1 → 0.4.0 and add a changelog/README note. **MINOR, non-breaking.**

## Capabilities

### New Capabilities
- `in-memory-sparql-datasource`: render reports against an in-process RDF graph (rdflib or a
  query callable), via a builder-injection seam on `ReportBuilder`, with templates unchanged
  and result shapes identical to the remote SPARQL source.

### Modified Capabilities
<!-- None: no existing spec carries requirements for these areas yet. -->

## Impact

- **Code**: `eds4jinja2/builders/report_builder.py` (constructor seam),
  `eds4jinja2/builders/jinja_builder.py` (optional builder registration), new
  `eds4jinja2/adapters/in_memory_sparql_ds.py`, new tests under `tests/unit/`.
- **APIs**: `ReportBuilder.__init__` gains two optional kwargs (additive). New public adapter
  class.
- **Dependencies**: none added (rdflib already present; pyoxigraph reached only via callable).
- **Version**: 0.3.1 → 0.4.0 (MINOR).
- **Golden thread / driver**: the consumer is the **rdf-differ `rdf-loading-module` epic** —
  its in-memory full-report capability depends on this enhancement; the integration point is
  the `from_endpoint` override described above.
