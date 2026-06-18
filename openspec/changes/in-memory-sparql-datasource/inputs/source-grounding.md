# Seed input — source grounding (preserved, never groomed)

Findings from reading the actual source on which the EPIC/PLAN are grounded.

- `builders/report_builder.py` (~L103): `ReportBuilder.__init__` calls
  `build_eds_environment(loader=template_loader, **self.template_flavour_syntax_spec)` — NO
  data-source-builder / filter injection. This is the missing seam.
- `builders/jinja_builder.py`: `DATA_SOURCE_BUILDERS` = `from_endpoint`
  (RemoteSPARQLEndpointDataSource), `from_file` (FileDataSource), `from_rdf_file`
  (RDFFileDataSource). `build_eds_environment(external_data_source_builders={**DATA_SOURCE_BUILDERS,
  **TABULAR_HELPERS, **TREE_HELPERS}, external_filters=ADDITIONAL_FILTERS, **kwargs)` — note the
  defaults REPLACE (not merge) the registries, so ReportBuilder must merge over defaults.
- `adapters/remote_sparql_ds.py`: `_fetch_tabular` → CSV → `pd.read_csv` (DataFrame);
  `_fetch_tree` → `setReturnFormat(JSON)` → `query.convert()` (SPARQL-JSON dict). Parity ref.
- `adapters/local_sparql_ds.py` (RDFFileDataSource): file-path only; `_fetch_tabular` calls
  `self.__graph__.parse(self.__filename__)` on EVERY query (re-parse smell); `_fetch_tree`
  raises `UnsupportedRepresentation` (tabular only — the tree gap).
- `adapters/base_data_source.py`: `DataSource` ABC — fail-safe `fetch_tabular`/`fetch_tree`
  returning `(result, error)`; abstract `_can_be_tabular/_can_be_tree/_fetch_tabular/_fetch_tree`.
- Version: `eds4jinja2/__init__.py` `__version__ = "0.3.1"`. rdflib already a dependency;
  pyoxigraph is NOT.
- Layers (config.yaml): `entrypoints > builders > adapters` (adapters innermost,
  import-linter enforced). pip + tox + pyproject; py311/py312.

Driver / golden thread: rdf-differ `rdf-loading-module` epic (in-memory full-report capability).
