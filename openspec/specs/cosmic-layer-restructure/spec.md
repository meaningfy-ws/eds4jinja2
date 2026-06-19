# cosmic-layer-restructure Specification

## Purpose
TBD - created by archiving change cosmic-layer-restructure. Update Purpose after archive.
## Requirements
### Requirement: The package is organised into the four Cosmic-Python layers

The `eds4jinja2` package SHALL be organised into four layers — `models`, `adapters`, `services`,
and `entrypoints` — with the documented contents: `models` holds pure, framework-free code in
four files — `models.sparql` (the pure SPARQL query-string builder, the substitution template,
and the SPARQL-result value objects), `models.data_source` (the `DataSource` ABC and
`UnsupportedRepresentation`, plus the `Engine` enum), `models.transformations` (the latex and
tabular transforms), and `models.collections` (the dict/list helpers); `adapters` holds I/O and
integration code (file, remote, local,
and in-memory SPARQL data sources, the graph store and its factory, the SPARQL query-file
reader, the namespace handler, the prefix.cc fetcher, and the HTTP source); `services` holds the
use-case orchestration (the Jinja builder, the report builder, the report-builder actions, and
the parallel executor); and `entrypoints` holds the `mkreport` CLI.

#### Scenario: Importing each layer module from its new path succeeds
- **WHEN** a module is imported from each layer's new path — `eds4jinja2.models.data_source`,
  `eds4jinja2.models.sparql`, `eds4jinja2.adapters.graph_store`,
  `eds4jinja2.services.report_builder`, and `eds4jinja2.entrypoints.cli.main`
- **THEN** every import resolves without error

#### Scenario: Pure helpers live under models, not adapters
- **WHEN** the pure helpers `escape_latex`, the tabular helpers, and the collection helpers
  (`invert_dict`, `deep_update`, `first_key`, `first_key_value`, `sort_by_size_and_alphabet`)
  are imported
- **THEN** they import from `eds4jinja2.models` (`models.transformations` and
  `models.collections`) and not from any `eds4jinja2.adapters` module

#### Scenario: The SPARQL boundary is split between pure and I/O
- **WHEN** the pure query helpers (`build_query`, `is_empty_query`, `EMPTY_QUERY_ERROR`) and the
  query-file reader (`read_query_file`) are imported
- **THEN** the pure helpers import from `eds4jinja2.models.sparql` and the file reader imports
  from `eds4jinja2.adapters.query_files`

### Requirement: The dependency direction is enforced by import-linter

The dependency direction SHALL be enforced by an import-linter contract set, available through a
`make check-architecture` target, encoding the layer law: `models` imports nothing from the
other three layers; `adapters` imports only from `models`; `services` imports from `adapters`
and `models`; and `entrypoints` imports from `services`.

#### Scenario: The restructured code passes the contract check
- **WHEN** `make check-architecture` (running `lint-imports`) is executed against the
  restructured package
- **THEN** all import-linter contracts pass and the command exits with success

#### Scenario: A forbidden import fails the contract check
- **WHEN** a `models` module is made to import an `adapters` (or `services` or `entrypoints`)
  module, or an `adapters` module is made to import a `services` (or `entrypoints`) module
- **THEN** `lint-imports` reports a contract violation and `make check-architecture` exits
  non-zero

### Requirement: The top-level public API remains stable across the move

The top-level `eds4jinja2` public API SHALL remain stable across the restructure: every name
previously exported from the `eds4jinja2` namespace SHALL still be importable from `eds4jinja2`
after the move, and the package `__all__` SHALL be unchanged.

#### Scenario: Previously-exported names still import from eds4jinja2
- **WHEN** the previously-exported names — `build_eds_environment`, `inject_environment_globals`,
  `FileDataSource`, `RemoteSPARQLEndpointDataSource`, `RDFFileDataSource`,
  `InMemorySPARQLDataSource`, `make_graph_store`, `RdflibGraphStore`, `OxigraphGraphStore`,
  `Engine`, `add_relative_figures`, `replace_strings_in_tabular`, `NamespaceInventory` — are
  imported from `eds4jinja2`
- **THEN** every name resolves and `eds4jinja2.__all__` equals the pre-change set

### Requirement: The version is bumped to 1.0.0 to signal the breaking move

The package version SHALL be bumped to `1.0.0` to signal the breaking deep-import-path move,
read from the single-source-of-truth `VERSION` file.

#### Scenario: VERSION reads 1.0.0
- **WHEN** the package version is read (via `eds4jinja2.__version__` or the `eds4jinja2/VERSION`
  file)
- **THEN** it is `1.0.0`

