## ADDED Requirements

### Requirement: Configurable parallelism with a sequential default

`ReportBuilder` SHALL read a `parallelism` integer from the report configuration, defaulting to `1`,
and SHALL behave exactly as the prior sequential renderer when `parallelism` is unset or `1`; when
`parallelism` is greater than `1` it SHALL fetch the report's data on up to that many concurrent
threads before rendering.

#### Scenario: Default or unset parallelism preserves sequential behaviour
- **WHEN** `make_document` is called with `parallelism` unset or set to `1`
- **THEN** the report is produced by the existing single sequential render with no record pass, no executor, and no temp folder created, byte-for-byte identical to the prior behaviour

#### Scenario: Parallelism greater than one fetches concurrently
- **WHEN** `make_document` is called with `parallelism` set to `N` greater than `1`
- **THEN** the report's data-fetch units are executed concurrently on up to `N` threads before the document is rendered

### Requirement: Pre-warm fetches in parallel, then render from cache

The library SHALL discover the report's data-fetch units (by a record pass over the template and/or
an explicit `prefetch` manifest), execute them in parallel before rendering, and render from the
resulting cache; a unit absent from the cache SHALL be fetched live during rendering.

#### Scenario: Recorded and manifested queries are fetched before rendering
- **WHEN** parallelism is enabled and the template's `fetch_*` calls (plus any `prefetch` manifest entries) are discovered
- **THEN** all discovered units are fetched concurrently and their results are staged in the cache before the real render begins

#### Scenario: Render consumes cached results
- **WHEN** the real render reaches a `fetch_*` call whose unit is in the cache
- **THEN** the cached result is served without issuing the query again

#### Scenario: A query not in the cache runs live
- **WHEN** the real render reaches a `fetch_*` call whose unit was not discovered during the record pass or manifest seeding
- **THEN** that query is fetched live during rendering, producing the correct result without aborting the report

### Requirement: All-or-nothing pre-warm execution

The parallel pre-warm SHALL be all-or-nothing: if any pre-warm fetch raises, the report SHALL be
aborted, no output file SHALL be written, and the error SHALL be surfaced; there SHALL be no retry,
no partial result, and no resume.

#### Scenario: A failed pre-warm fetch aborts the whole report
- **WHEN** parallelism is enabled and one pre-warm fetch raises an exception
- **THEN** the report is aborted, no output file is written, and the error is surfaced to the caller

### Requirement: Temp-folder cache is always cleaned up

When parallelism is enabled, pre-warm results SHALL be staged in a temporary folder, and that folder
SHALL be removed after rendering completes — both on a successful render and on an aborted run.

#### Scenario: Temp folder removed after a successful render
- **WHEN** parallelism is enabled and the report renders successfully
- **THEN** the temporary cache folder is removed once rendering finishes

#### Scenario: Temp folder removed after an aborted run
- **WHEN** parallelism is enabled and the run is aborted by a failing pre-warm fetch
- **THEN** the temporary cache folder is still removed

### Requirement: Concurrent queries to the same SPARQL endpoint are isolated

The remote SPARQL data source SHALL allow concurrent queries to the same endpoint without sharing
mutable query state, so that two threads querying one endpoint with different queries each obtain
their own correct results.

#### Scenario: Two threads query one endpoint with different queries
- **WHEN** two threads each set a different query on the same endpoint URL and fetch concurrently
- **THEN** each thread obtains the result of its own query, with neither query string clobbering the other

### Requirement: Identical queries are fetched once

When the same `(source, query)` pair appears more than once within a single report run, the library
SHALL execute it only once, keying the cache by the source identity and the normalised query.

#### Scenario: A repeated source-and-query is executed a single time
- **WHEN** parallelism is enabled and the same source with the same normalised query is requested twice in one report
- **THEN** the query is executed once and both requests are served from the same cached result
