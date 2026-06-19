## ADDED Requirements

### Requirement: Built-in graph store loads RDF sources with a configurable engine

The library SHALL provide a built-in graph store that loads one or more RDF sources (file paths or
URLs) into an in-memory graph and queries it, with the engine selectable through an `Engine`
enumeration whose default is `rdflib` and whose `oxigraph` value is an opt-in extra. The store
MUST NOT require any external SPARQL server. The engine MUST be chosen from the enumeration; a
template- or caller-supplied engine value MUST be converted at the boundary so that unknown values
are rejected. `pyoxigraph` MUST NOT be imported on the `rdflib` path nor at module import time.

#### Scenario: Load a single source
- **WHEN** a graph store is built with a single RDF source (a file path or a URL)
- **THEN** that source is parsed into the in-memory graph and SPARQL queries are answered from it

#### Scenario: Load multiple sources into one graph
- **WHEN** a graph store is built with a list of RDF sources
- **THEN** all sources are parsed into a single in-memory graph and queries see their union

#### Scenario: rdflib is the default engine
- **WHEN** a graph store is built without specifying an engine
- **THEN** the `rdflib` engine is used and no `pyoxigraph` import occurs

#### Scenario: oxigraph engine used when requested and installed
- **WHEN** a graph store is built with `engine="oxigraph"` and `pyoxigraph` is installed
- **THEN** the oxigraph-backed store loads the sources and answers queries

#### Scenario: oxigraph requested but not installed
- **WHEN** a graph store is built with `engine="oxigraph"` and `pyoxigraph` is not installed
- **THEN** construction raises a clear, actionable error instructing the caller to install `eds4jinja2[oxigraph]`

#### Scenario: Unknown engine is rejected
- **WHEN** a graph store is requested with an engine value that is not in the `Engine` enumeration
- **THEN** a `ValueError` is raised at the boundary before any source is loaded

### Requirement: The `from_rdf` builder queries the loaded graph with tabular and tree parity

The library SHALL register a `from_rdf` template builder that accepts one source or a list of
sources and an optional engine (defaulting to `rdflib`), builds a built-in graph store, and wraps
its query capability in an `InMemorySPARQLDataSource`. The results SHALL provide both tabular and
tree representations with shapes identical to the in-memory SPARQL data source, for both engines.
The `from_rdf` builder SHALL supersede the legacy `from_rdf_file` builder without removing or
changing it.

#### Scenario: SELECT returns a tabular DataFrame
- **WHEN** a `from_rdf(...)` source has a SELECT query set and tabular data is fetched
- **THEN** a pandas `DataFrame` of stringified bindings is returned, matching the in-memory SPARQL data source shape

#### Scenario: SELECT returns tree SPARQL-JSON
- **WHEN** a `from_rdf(...)` source has a SELECT query set and tree data is fetched
- **THEN** a dict is returned with a `head.vars` list and a `results.bindings` list whose entries map each variable to a `{"type": ..., "value": ...}` object

#### Scenario: Legacy builder remains available
- **WHEN** the data-source builder registry is inspected after `from_rdf` is registered
- **THEN** the legacy `from_rdf_file` builder is still present and its behaviour is unchanged

### Requirement: Sources are loaded once and reused across queries

The built-in graph store SHALL parse each source exactly once at construction and reuse the loaded
graph for every subsequent query, instead of re-parsing per query as the legacy file-based source
does.

#### Scenario: Two queries parse the sources only once
- **WHEN** two SPARQL queries are executed against the same `from_rdf(...)` source
- **THEN** each underlying RDF source is parsed exactly once (no per-query re-parse)

### Requirement: Stores are safe for concurrent reads

The built-in graph store SHALL be safe for concurrent read queries after loading, so that a future
parallel report executor can issue queries from multiple threads. The store MUST NOT expose any
write or update operation.

#### Scenario: Concurrent read queries return correct results
- **WHEN** multiple threads issue read queries against the same loaded `from_rdf(...)` store at the same time
- **THEN** each query returns correct results with no corruption or interference
