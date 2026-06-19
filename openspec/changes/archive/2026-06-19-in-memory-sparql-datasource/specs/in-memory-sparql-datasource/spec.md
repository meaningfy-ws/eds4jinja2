## ADDED Requirements

### Requirement: ReportBuilder accepts injected data-source builders and filters

The `ReportBuilder` constructor SHALL accept optional `external_data_source_builders` and
`external_filters` mapping arguments, defaulting to empty mappings, and SHALL forward them
(merged over the framework's default builders, tabular/tree helpers, and additional filters)
into the Jinja environment so that injected entries override defaults of the same name.

#### Scenario: Injected builder overrides the default
- **WHEN** a `ReportBuilder` is constructed with `external_data_source_builders` containing a `from_endpoint` entry
- **THEN** the Jinja environment exposes the injected `from_endpoint` builder in place of the default `RemoteSPARQLEndpointDataSource` builder

#### Scenario: Default behaviour preserved when nothing is injected
- **WHEN** a `ReportBuilder` is constructed without `external_data_source_builders` or `external_filters`
- **THEN** the Jinja environment exposes exactly the framework's default builders and filters, unchanged from prior behaviour

#### Scenario: Default helpers preserved alongside a partial injection
- **WHEN** a `ReportBuilder` is constructed with only a single injected builder (e.g. `from_endpoint`)
- **THEN** the default builders, tabular/tree helpers, and additional filters (e.g. `from_file`, `invert_dict`, `escape_latex`) remain available in the environment

### Requirement: In-memory SPARQL data source serves an in-process graph

The library SHALL provide an `InMemorySPARQLDataSource` that is a `DataSource` and that accepts
either an `rdflib.Graph` or a `query(sparql_text)` callable as its source, evaluating SPARQL
queries in memory without any external SPARQL server or file I/O.

#### Scenario: Construct from an rdflib.Graph
- **WHEN** an `InMemorySPARQLDataSource` is constructed with an `rdflib.Graph`
- **THEN** it answers SPARQL queries using that graph's own query capability

#### Scenario: Construct from a query callable
- **WHEN** an `InMemorySPARQLDataSource` is constructed with a `query(sparql_text)` callable (e.g. a pyoxigraph-backed store)
- **THEN** it answers SPARQL queries by invoking that callable

#### Scenario: Invalid source is rejected
- **WHEN** an `InMemorySPARQLDataSource` is constructed with something that is neither an `rdflib.Graph` nor a callable
- **THEN** construction raises a `TypeError`

### Requirement: In-memory tabular results match the remote source shape

`InMemorySPARQLDataSource` SHALL implement tabular fetching that returns a pandas `DataFrame`
of stringified bindings, with the same structure produced by the remote SPARQL data source.

#### Scenario: Tabular fetch returns a DataFrame
- **WHEN** a SELECT query is set via `with_query` and tabular data is fetched
- **THEN** a pandas `DataFrame` is returned whose columns are the query's bound variables and whose cells are the stringified bound values

#### Scenario: Empty result set
- **WHEN** a SELECT query that binds nothing is fetched as tabular
- **THEN** an empty `DataFrame` is returned without error

### Requirement: In-memory tree results match the SPARQL-JSON shape

`InMemorySPARQLDataSource` SHALL implement tree fetching that returns the SPARQL 1.1 JSON
results object (`{"head": {"vars": [...]}, "results": {"bindings": [...]}}`), with the same
structure produced by the remote SPARQL data source — explicitly closing the tree gap of the
file-based RDF data source.

#### Scenario: Tree fetch returns SPARQL-JSON
- **WHEN** a SELECT query is set and tree data is fetched
- **THEN** a dict is returned with a `head.vars` list and a `results.bindings` list whose entries map each variable to a `{"type": ..., "value": ...}` object

#### Scenario: Term typing
- **WHEN** a binding value is a URI, a literal, or a blank node
- **THEN** its entry carries the corresponding `type` (`uri`, `literal`, `bnode`), and literals carry their datatype or language when present

### Requirement: Empty-query and engine errors are handled fail-safe

`InMemorySPARQLDataSource` SHALL raise on fetching when no query has been set, and the
inherited fail-safe wrappers SHALL convert fetch errors into a `(None, error_message)` result.

#### Scenario: Fetching without a query
- **WHEN** tabular or tree data is fetched before any query is set
- **THEN** the underscored fetch raises an exception and the public `fetch_*` wrapper returns `(None, <error message>)`

### Requirement: Reports render in memory with templates unchanged

A consumer SHALL be able to render an existing report whose templates call
`from_endpoint(...)` against an in-process graph, with no change to the templates, by injecting
a `from_endpoint` builder that returns an `InMemorySPARQLDataSource`.

#### Scenario: Server-less rendering of an unchanged template
- **WHEN** a `ReportBuilder` is constructed with `external_data_source_builders={"from_endpoint": lambda _endpoint: InMemorySPARQLDataSource(graph)}` and `make_document` is called
- **THEN** the report is produced from the in-process graph with no SPARQL server running and with the template files unchanged
