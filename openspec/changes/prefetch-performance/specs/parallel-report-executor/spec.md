## RENAMED Requirements

- FROM: `### Requirement: Temp-folder cache is always cleaned up`
- TO: `### Requirement: The fetch cache is in memory by default and always cleaned up`

## MODIFIED Requirements

### Requirement: Configurable parallelism with a sequential default

`ReportBuilder` SHALL read a `parallelism` integer from the report configuration, defaulting to `1`.
When `parallelism` is unset or `1` it SHALL render with no record pass and no thread pool, producing
the same output as the prior sequential renderer for deterministic queries, with identical fetches memoised as the requirement
"Identical queries are fetched once" states. When `parallelism` is greater than `1` it SHALL fetch the
report's data on up to that many concurrent threads before rendering.

#### Scenario: Default or unset parallelism preserves sequential output
- **WHEN** `make_document` is called with `parallelism` unset or set to `1`
- **THEN** the report is produced by a single sequential render with no record pass and no thread pool, and, for deterministic queries, its content equals the prior sequential output

#### Scenario: Parallelism greater than one fetches concurrently
- **WHEN** `make_document` is called with `parallelism` set to `N` greater than `1`
- **THEN** the report's data-fetch units are executed concurrently on up to `N` threads before the document is rendered

### Requirement: The fetch cache is in memory by default and always cleaned up

The cache that holds pre-warmed and memoised fetch results SHALL be kept in memory unless the report
configuration sets `prefetch_cache` to `disk`, in which case results SHALL be staged in a temporary
folder. The configuration value SHALL be `memory` (the default) or `disk`; any other value SHALL raise
`ValueError` naming `prefetch_cache` when the `ReportBuilder` is created. The cache SHALL hold
results for one render or one batch only, and SHALL be emptied (memory) or removed (disk) when that
render or batch ends — on success and on an aborted run.

#### Scenario: Memory cache by default
- **WHEN** a report is rendered with `parallelism` 4 and no `prefetch_cache` setting
- **THEN** no temporary cache folder is created

#### Scenario: Temp folder removed after a successful render
- **WHEN** `prefetch_cache` is `disk`, parallelism is enabled and the report renders successfully
- **THEN** a temporary cache folder was used and is removed once rendering finishes

#### Scenario: Temp folder removed after an aborted run
- **WHEN** `prefetch_cache` is `disk`, parallelism is enabled and the run is aborted by a failing pre-warm fetch
- **THEN** the temporary cache folder is still removed

#### Scenario: Unknown cache medium
- **WHEN** a `ReportBuilder` is created with `prefetch_cache` set to `ram`
- **THEN** `ValueError` is raised naming `prefetch_cache` and the allowed values, and nothing is rendered or fetched

### Requirement: Identical queries are fetched once

The library SHALL execute an identical fetch — the same data-source builder (one of the framework's
`DATA_SOURCE_BUILDERS` names, including a consumer's override of one) with the same arguments, the
same query and the same fetch method — at most once within one render or one batch, with or
without parallelism, keying the cache by the source identity, the query and the method. Every later
identical request SHALL receive a copy of the stored result, so that changing it in place does not
change what later requests receive. A fetch that returns an error SHALL NOT be stored: the next
identical request SHALL run it again. Nothing SHALL be cached across renders or batches.

#### Scenario: A repeated source-and-query is executed a single time
- **WHEN** parallelism is enabled and the same source with the same query is requested twice in one report
- **THEN** the query is executed once and both requests are served the same result

#### Scenario: A query repeated in a sequential report
- **GIVEN** `parallelism` unset and a template that fetches the same query three times
- **WHEN** `make_document` is called
- **THEN** the query is executed once

#### Scenario: A stored result is a copy
- **GIVEN** a template that fetches a table, removes its rows in place, then fetches the same query again
- **WHEN** the report is rendered, with `parallelism` 1 and with `parallelism` 4
- **THEN** the second fetch returns all the rows

#### Scenario: A failed fetch is retried
- **GIVEN** `parallelism` unset and a data source whose first call fails and second succeeds
- **WHEN** a template fetches the same query twice
- **THEN** the source was called twice and the second call's result reached the template

#### Scenario: No cache between renders
- **WHEN** the same `ReportBuilder` renders the same report twice
- **THEN** each render executes its fetches again
