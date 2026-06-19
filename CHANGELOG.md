# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-06-19

### Fixed
- **Logging no longer hijacks the root logger.** Importing `eds4jinja2` previously added a
  `StreamHandler` to the *root* logger and forced `INFO` level — affecting every consumer and
  duplicating output. The library now attaches only a `NullHandler` to its package logger;
  applications own logging configuration, and the `mkreport` CLI configures logging itself.

### Changed
- Fail-safe data-source fetches now log handled failures (e.g. `UnsupportedRepresentation`, empty
  query) at **WARNING with the message** instead of ERROR with a full stack trace.

## [1.0.0] - 2026-06-19

First major release. Adds in-memory RDF reporting and opt-in parallel execution, and realigns the
package onto enforced Cosmic-Python layers. The top-level `eds4jinja2` public API is unchanged;
only deep import paths moved (see **Migration**).

### Added
- **In-memory graph data sources** — render reports against an in-process RDF graph, no SPARQL
  server required:
  - `from_graph(...)` (alias `from_memory`) — query an `rdflib.Graph`, a `pyoxigraph` store, or any
    `query(sparql)` callable you already hold.
  - `from_rdf(sources, engine="rdflib")` — load one or more RDF files/URLs into an in-memory graph
    (engine `rdflib` by default, or `oxigraph`) and query it. Tabular **and** tree (SPARQL-JSON)
    results; loads each source once.
  - `InMemorySPARQLDataSource` (engine-agnostic) and a built-in graph store (`make_graph_store`,
    `RdflibGraphStore`, `OxigraphGraphStore`, `Engine`).
- **Builder-injection seam** — `ReportBuilder(external_data_source_builders=..., external_filters=...)`,
  merged over the defaults, so a consumer can override e.g. `from_endpoint` to serve an in-memory
  graph with the templates unchanged.
- **Parallel report execution** — opt-in via the `parallelism` config key: threads-only pre-warm of
  all data fetches before rendering, all-or-nothing, with a temp-folder cache. Off by default
  (`parallelism` unset/`1` is the previous sequential behaviour).
- **Optional `oxigraph` extra** — `pip install eds4jinja2[oxigraph]` for the fast in-memory engine.
- **Architecture enforcement** — `.importlinter` layer contracts and a `make check-architecture`
  target.

### Changed
- **BREAKING — package restructured into Cosmic-Python layers** `models / adapters / services /
  entrypoints` (was `adapters / builders / entrypoints`). Deep import paths moved — see Migration.
- SPARQL query results are now modelled with **Pydantic** (added as a runtime dependency); the
  result shape returned to templates is unchanged.
- The remote SPARQL connection pool is now **thread-safe** (per-thread wrappers), enabling parallel
  execution.
- De-duplicated SPARQL query-string building and centralised the SPARQL-JSON keys.
- The package version is now a single source of truth in the `eds4jinja2/VERSION` file.
- Unit tests reorganised into per-layer folders isomorphic to the package.

### Migration (0.3.1 → 1.0.0)
- **No change** for the top-level namespace: `from eds4jinja2 import RemoteSPARQLEndpointDataSource,
  RDFFileDataSource, FileDataSource, build_eds_environment, ...` still work.
- **Deep imports moved** (no deprecation shims — update them directly):
  - `eds4jinja2.builders.*` → `eds4jinja2.services.*`
    (e.g. `eds4jinja2.builders.report_builder` → `eds4jinja2.services.report_builder`).
  - `eds4jinja2.adapters.base_data_source` → `eds4jinja2.models.data_source`.
  - `eds4jinja2.adapters.latex_utils` / `tabular_utils` → `eds4jinja2.models.transformations`.
  - `eds4jinja2.adapters.sparql_results` / `substitution_template`, and the pure query helpers of
    `sparql_query` → `eds4jinja2.models.sparql`; `read_query_file` → `eds4jinja2.adapters.query_files`.
  - the dict/list helpers (`invert_dict`, `deep_update`, ...) → `eds4jinja2.models.collections`.

## [0.3.1] - 2026-06-18
- Modernised packaging (pip + `pyproject.toml`, setuptools backend; Python 3.11/3.12) and CI.

[Unreleased]: https://github.com/meaningfy-ws/eds4jinja2/compare/1.0.1...HEAD
[1.0.1]: https://github.com/meaningfy-ws/eds4jinja2/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/meaningfy-ws/eds4jinja2/compare/0.3.1...1.0.0
[0.3.1]: https://github.com/meaningfy-ws/eds4jinja2/releases/tag/0.3.1
