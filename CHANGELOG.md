# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2026-10-31

### Added
- `ReportBuilder.render_documents(outputs, *, autoescape=None)` renders the configured template once
  per named output, each with its own template variables, and returns _name → text_ in memory. It
  writes no file and runs no listener. The batch is checked before anything is rendered: output names
  must stay inside the output folder and must not clash (two names of one file, a name that is the
  folder of another, or a name under an existing file), and a template variable may not hide an environment global such as `conf` or
  `from_endpoint`. Autoescaping can be set per batch without changing the builder's
  environment. It uses the parallel pre-fetch when `parallelism` > 1. (OpenSpec change
  `render-documents`)
- `ReportBuilder.make_documents(outputs, *, check=None, autoescape=None)` renders a batch the same
  way, passes each text to `check(name, text)`, and writes the files only if every check passes. It
  writes them as UTF-8, with no newline translation, under the output folder and returns their
  absolute paths in order. The rendering
  listeners run once per batch. The after-rendering listeners do not run when a check fails. The
  writes are not atomic: a disk error partway through can leave some files. (OpenSpec change
  `make-documents`)

## [2.0.0] - 2026-10-30

Modernization release (OpenSpec change `modernize-library-py312`). Python 3.11 users: pin
`eds4jinja2<2` — 1.x stays on PyPI.

### Breaking
- **Python 3.12+ required** (`requires-python >=3.12`); tested on 3.12, 3.13 and 3.14.
- **pandas 3 / numpy 2.** Tabular results are pandas 3 DataFrames: text columns have the `str`
  dtype instead of `object`. Code that selects text columns with `select_dtypes(object)` should use
  `select_dtypes([object, "str"])`.
- **Dependencies no longer installed with eds4jinja2:** `xlrd`, `openpyxl` (replaced by
  `python-calamine`, which reads `.xls` and `.xlsx`), `toml` (stdlib `tomllib` is used),
  `py-singleton`, `beautifulsoup4`. Install them yourself if your code imports them.
- `SPARQLClientPool.instance()` is gone (it came from the removed `@singleton` decorator); the pool
  was always used through its static `create_or_reuse_connection`.

### Fixed
- Reading `.toml` files through `FileDataSource` works; it passed bytes to `toml.loads` and failed.

### Changed
- Runtime dependencies upgraded: pandas 2.2 → 3.1, numpy 1.26 → 2.5, rdflib 7.0 → 7.6,
  click 8.1 → 8.5, requests 2.31 → 2.34, pyoxigraph 0.4 → 0.5 (`oxigraph` extra). Runtime
  requirements are now major-version ranges (`>=X.Y,<X+1`) instead of patch-level pins.
- `build_eds_environment(...)`, `ReportBuilder(additional_config=...)` and
  `make_pdf_from_latex(...)` take `None` defaults instead of shared mutable defaults; calls without
  those arguments behave as before.
- Excel files are read with pandas' `calamine` engine (the `xlrd` engine is deprecated in pandas 3).

### Development
- Packaging moved from setuptools + pip + tox to **Poetry** (committed `poetry.lock`).
- New gate `make check-all`, run on every pull request: Ruff (lint + format), mypy, import-linter
  (now also forbidding I/O and framework imports in `models` and `services`), `openspec validate
  --strict`, and the test suite. Test tooling upgraded to pytest 9.1, pytest-bdd 9, pytest-cov 7.
- `AGENTS.md` is the canonical agent file; `CLAUDE.md` imports it. `SECURITY.md` added.

## [1.0.4] - 2026-06-20

### Added
- **Mermaid diagrams** in the explanatory documentation pages (render-time data-fetch sequence, the
  Cosmic-Python layer dependencies, the parallel pre-warm pipeline, and the builder-injection seam)
  via the Antora Mermaid extension.

### Removed
- **Dropped ReadTheDocs.** The documentation is now published to **GitHub Pages only**
  (https://meaningfy-ws.github.io/eds4jinja2/). The RTD build had been dead since 2022, so
  `.readthedocs.yml` is removed and the README/badge point at GitHub Pages. No package code change.

## [1.0.3] - 2026-06-19

### Changed
- **Documentation migrated from Sphinx to AsciiDoc + Antora** (the Meaningfy house standard). The
  single `index.rst` page is restructured into a navigable, searchable multi-page site (getting
  started, every data source, in-memory graphs, parallel execution, templating, CLI, a curated
  public-API reference, extending, architecture). The build is now a first-class local + CI concern:
  `make build-docs` / `preview-docs`, a GitHub Actions workflow that builds on every PR and deploys
  to **GitHub Pages** (`https://meaningfy-ws.github.io/eds4jinja2/`), and ReadTheDocs building the
  same Antora playbook so the existing `readthedocs.io` URL keeps working.

### Removed
- The Sphinx stack (`docs/conf.py`, `docs/index.rst`, `docs/srcdocs/`, `docs/Makefile`,
  `docs/make.bat`) and the Python `docs` extra (`Sphinx`, `myst-parser`, `sphinxcontrib-apidoc`).
  No change to the `eds4jinja2` package code, public API, or behaviour.

## [1.0.2] - 2026-06-19

### Fixed
- README: the PyPI version/status badges were stuck (cached on shields' CDN) showing `0.3.1` /
  `alpha`; the badge URLs are cache-busted so they reflect the current release.

### Changed
- Test suite hardened against external volatility: the live DESCRIBE test no longer asserts an
  exact (drifting) triple count, and the flaky `httpbin.org/status/500` example was removed from
  the SPARQL-error feature. No library code change.

## [1.0.1] - 2026-06-19

### Fixed
- **Logging no longer hijacks the root logger.** Importing `eds4jinja2` previously added a
  `StreamHandler` to the *root* logger and forced `INFO` level — affecting every consumer and
  duplicating output. The library now attaches only a `NullHandler` to its package logger;
  applications own logging configuration, and the `mkreport` CLI configures logging itself.

### Changed
- Fail-safe data-source fetches now log handled failures (e.g. `UnsupportedRepresentation`, empty
  query) at **WARNING with the message** instead of ERROR with a full stack trace.
- Docs/tests: README rewritten (why / what it solves / how to use, data-source table); the
  `RDFFileDataSource` unit tests now assert on real query results and `make_document` is tested
  offline (no live SPARQL endpoint in the default test gate).

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

[Unreleased]: https://github.com/meaningfy-ws/eds4jinja2/compare/2.0.0...HEAD
[2.0.0]: https://github.com/meaningfy-ws/eds4jinja2/compare/1.0.4...2.0.0
[1.0.4]: https://github.com/meaningfy-ws/eds4jinja2/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/meaningfy-ws/eds4jinja2/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/meaningfy-ws/eds4jinja2/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/meaningfy-ws/eds4jinja2/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/meaningfy-ws/eds4jinja2/compare/0.3.1...1.0.0
[0.3.1]: https://github.com/meaningfy-ws/eds4jinja2/releases/tag/0.3.1
