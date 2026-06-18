# Seed input — source grounding (preserved, never groomed)

Findings from reading the actual source on which the EPIC/PLAN are grounded.

- `builders/jinja_builder.py`: `DATA_SOURCE_BUILDERS` registry maps template-callable names to
  data-source builder lambdas:
  ```python
  DATA_SOURCE_BUILDERS = {
      "from_endpoint": lambda endpoint: RemoteSPARQLEndpointDataSource(endpoint),
      "from_file":     lambda file_path: FileDataSource(file_path),
      "from_rdf_file": lambda from_rdf_file: RDFFileDataSource(from_rdf_file),
  }
  ```
  This is the seam where a new `from_rdf` builder is registered (additive — does not touch the
  existing keys). `build_eds_environment(external_data_source_builders={**DATA_SOURCE_BUILDERS,
  **TABULAR_HELPERS, **TREE_HELPERS}, external_filters=ADDITIONAL_FILTERS, **kwargs)` — defaults
  REPLACE (not merge) the registries.

- `adapters/local_sparql_ds.py` (`RDFFileDataSource`) — the legacy source this change supersedes
  WITHOUT removing:
  - constructor takes a single `filename` (file path ONLY — no URL support, no graph hand-in);
  - `_fetch_tabular` calls `self.__graph__.parse(self.__filename__)` on **every** query — this is
    the re-parse-per-query smell the new built-in store fixes by loading once at construction;
  - `_fetch_tree` raises `UnsupportedRepresentation("Only TABULAR representation is supported")`
    — tabular-only, the tree gap;
  - `with_query(...)` raises if the query was already set; uses `SubstitutionTemplate`.

- `adapters/base_data_source.py` (`DataSource` ABC): fail-safe wrappers `fetch_tabular` /
  `fetch_tree` return `(result, error)` and catch every `Exception` (→ `(None, str(e))`); the
  four abstract methods are `_can_be_tabular`, `_can_be_tree`, `_fetch_tabular`, `_fetch_tree`.
  Any error raised by a graph store (missing file, parse failure, engine error) propagates
  through `_fetch_*` and is caught by these wrappers — no new error plumbing needed.

- `adapters/remote_sparql_ds.py` (`RemoteSPARQLEndpointDataSource`): `_fetch_tabular` → CSV →
  `pd.read_csv` (DataFrame); `_fetch_tree` → `setReturnFormat(JSON)` → `query.convert()`
  (SPARQL-JSON dict). This is the parity reference for result shapes — but in THIS change the
  shapes come for free from `InMemorySPARQLDataSource` (sibling change), not from re-derived code.

- Sibling change `in-memory-sparql-datasource` (read in full): provides
  `InMemorySPARQLDataSource(DataSource)`, engine-agnostic — accepts an `rdflib.Graph` OR a
  `query(sparql_text) -> results` callable — and implements BOTH `_fetch_tabular` (DataFrame of
  stringified bindings) and `_fetch_tree` (SPARQL-JSON dict), with a normaliser that consumes
  rdflib `Result` objects and pyoxigraph-style solutions. The sibling's No-gos state **"No
  `pyoxigraph` import in `eds4jinja2`"**. This change deliberately and narrowly relaxes that, as
  an OPT-IN extra only (see DEC-3 / reconciliation note in proposal.md).

- `pyproject.toml`: `[project.optional-dependencies]` already groups `test`, `docs`, `dev`
  extras; `requests~=2.31.0` and `rdflib~=7.0.0` are already runtime dependencies. The new
  `oxigraph` extra (`pyoxigraph~=0.4`) follows the same pattern. `requests` (already present) is
  used to fetch remote RDF bytes for the oxigraph engine (pyoxigraph `Store.load` has no native
  HTTP fetch; rdflib `graph.parse` does).

- Version: `eds4jinja2/__init__.py` `__version__ = "0.3.1"`. This change is a MINOR bump
  (additive, non-breaking). Exact number depends on ship order relative to the in-memory core
  (the sibling change also bumps MINOR) — state "next MINOR".

- Layers (config.yaml): `entrypoints > builders > adapters` (adapters innermost, import-linter
  enforced). The new `graph_store.py` lives in `adapters/` and imports nothing upward. pip + tox
  + pyproject; py311/py312.

Driver / golden thread: this is the file-loading layer ON TOP OF the sibling
`in-memory-sparql-datasource` change — Scenario 1 is "generate a report directly from RDF
files, no SPARQL server, no consumer-written loading code". A separate future
`parallel-report-executor` change motivates the concurrent-read-safety forward-compat note.
