## MODIFIED Requirements

### Requirement: Pre-warm fetches in parallel, then render from cache

The library SHALL discover the report's data-fetch units by a record pass over the template, execute
them in parallel before rendering, and render from the resulting cache; a unit absent from the cache
SHALL be fetched live during rendering.

#### Scenario: Recorded queries are fetched before rendering
- **WHEN** parallelism is enabled and the template's `fetch_*` calls are discovered by the record pass
- **THEN** all discovered units are fetched concurrently and their results are staged in the cache before the real render begins

#### Scenario: Render consumes cached results
- **WHEN** the real render reaches a `fetch_*` call whose unit is in the cache
- **THEN** the cached result is served without issuing the query again

#### Scenario: A query not in the cache runs live
- **WHEN** the real render reaches a `fetch_*` call whose unit was not discovered during the record pass
- **THEN** that query is fetched live during rendering, producing the correct result without aborting the report
