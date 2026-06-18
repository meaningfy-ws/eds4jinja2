# Seed input — source grounding (preserved, never groomed)

Findings from reading the actual source on which the EPIC/PLAN are grounded.

- `builders/report_builder.py` (~L134-144): `ReportBuilder.make_document` is the single
  orchestration point. It does `template = self.__get_template(...)`, makes the output folder, then
  `template.stream().dump(<output_folder>/<template>)` — ONE sequential render in document order.
  This is where the pre-warm (record → parallel fetch → render-from-cache → cleanup) is added.
  Constructor at ~L57 already accepts `additional_config`; `before`/`after` rendering listeners exist
  (`add_after_rendering_listener` is used to copy static files) — a natural seam for cleanup too.
- `builders/jinja_builder.py`: `DATA_SOURCE_BUILDERS` = `from_endpoint`
  (`lambda endpoint: RemoteSPARQLEndpointDataSource(endpoint)`), `from_file` (FileDataSource),
  `from_rdf_file` (RDFFileDataSource). Templates call `from_endpoint(url).with_query(q).fetch_tabular()`.
  These builders must become cache-aware (RECORD/SERVE/LIVE) without changing template syntax.
- `adapters/remote_sparql_ds.py`: CRITICAL thread-safety defect. `SPARQLClientPool` is a `@singleton`
  whose `create_or_reuse_connection(endpoint_url)` stores and returns ONE shared `SPARQLWrapper` per
  URL. `RemoteSPARQLEndpointDataSource.with_query` calls `self.endpoint.setQuery(new_query)` and
  `_fetch_tree`/`_fetch_tabular` read `self.endpoint.queryString`. Concurrent queries to the same
  endpoint clobber each other's query string. Fixing this (per-call or per-thread `SPARQLWrapper`) is
  a prerequisite of this change. `_fetch_tree` → `setReturnFormat(JSON)` + `query.convert()`;
  `_fetch_tabular` → `setReturnFormat(CSV)` + `pd.read_csv`. `__str__` reads `endpoint`/`queryString`.
- `adapters/base_data_source.py`: `DataSource` ABC — fail-safe `fetch_tabular`/`fetch_tree` wrap the
  underscored `_fetch_*` and return `(result, error)`; abstract
  `_can_be_tabular`/`_can_be_tree`/`_fetch_tabular`/`_fetch_tree`. This `(result, error)` contract must
  be preserved by the cache-aware SERVE/LIVE paths.
- Version: `eds4jinja2/__init__.py` `__version__ = "0.3.1"`. stdlib `concurrent.futures` available;
  no new mandatory dependency for the default executor.
- Layers (config.yaml): `entrypoints > builders > adapters` (adapters innermost, import-linter
  enforced). The executor port and prefetch cache live in `builders` (may use `adapters`, never the
  reverse). pip + tox + pyproject; py311/py312.

Hard truth to encode: Jinja2 `template.stream()` evaluates in document order and cannot be
parallelised — the only lever is decoupling DATA FETCHING from rendering. Threads only: remote
endpoints and oxigraph release the GIL (real speedup); rdflib in-memory is pure-Python/GIL-bound
(limited speedup, still correct). Processes/Celery rejected — cannot cheaply share an in-memory graph.

Driver / golden thread: rdf-differ's long-running report generation (30+ min reports). Builds on
`in-memory-sparql-datasource` (data sources safe for concurrent reads) and is complementary to
`builtin-graph-store` (oxigraph in-memory is where threading pays off for in-memory graphs).
