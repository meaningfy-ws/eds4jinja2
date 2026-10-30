<!-- Capability: parallel-report-executor. EPIC: parallel-executor-hardening (proposal.md). -->

## MODIFIED Requirements

### Requirement: Pre-warm fetches in parallel, then render from cache

The library SHALL discover the report's data-fetch units by record passes over the template,
execute them in parallel before rendering, and render from the resulting cache; a unit absent from
the cache SHALL be fetched live during rendering. (The optional `prefetch` manifest is withdrawn —
DEC-4.)

#### Scenario: Recorded queries are fetched before rendering
- **WHEN** parallelism is enabled and the template's `fetch_*` calls are discovered by the record passes
- **THEN** all discovered units are fetched concurrently and their results are staged in the cache before the real render begins

#### Scenario: Render consumes cached results
- **WHEN** the real render reaches a `fetch_*` call whose unit is in the cache
- **THEN** the cached result is served without issuing the query again

#### Scenario: A query not in the cache runs live
- **WHEN** the real render reaches a `fetch_*` call whose unit was not discovered by any record pass
- **THEN** that query is fetched live during rendering, producing the correct result without aborting the report

## ADDED Requirements

### Requirement: Discovery proceeds in waves

When parallelism is enabled, the library SHALL repeat the record pass in waves: each record pass
SHALL serve units already in the cache with their real result and only unknown units with a
placeholder, and the units newly discovered by a wave SHALL be pre-warmed in parallel before the
next wave. Discovery SHALL stop when a wave discovers no new unit or when `prewarm_max_waves`
(default `5`) waves have run.

#### Scenario: A data-dependent query is pre-warmed in the second wave
- **GIVEN** a template that fetches a list of items and then issues one query per item
- **WHEN** the report is built with parallelism enabled
- **THEN** the list query is pre-warmed in wave 1, the per-item queries are pre-warmed concurrently in wave 2, and the real render issues no live fetch

#### Scenario: Discovery stops when nothing new is found
- **GIVEN** a template whose queries do not depend on fetched data
- **WHEN** the report is built with parallelism enabled
- **THEN** wave 2 discovers no new unit and discovery stops after it

#### Scenario: Discovery stops at the wave cap
- **GIVEN** `prewarm_max_waves` set to `2` and a template with three levels of dependent queries
- **WHEN** the report is built with parallelism enabled
- **THEN** only two waves run, the third-level queries are fetched live during the real render, and the output equals the sequential render

### Requirement: A record-pass error does not abandon parallelism

If a record pass raises, the units recorded before the error SHALL still be pre-warmed and
discovery SHALL continue with the next wave. When a wave raises and discovers no new unit,
discovery SHALL stop and the report SHALL proceed to the real render, which surfaces any genuine
template error.

#### Scenario: A placeholder-induced error is overcome by real data
- **GIVEN** a template that indexes the first row of a fetched result
- **WHEN** the report is built with parallelism enabled
- **THEN** wave 1 raises on the empty placeholder, its recorded units are pre-warmed, wave 2 completes with real data, and the report is produced from the cache

#### Scenario: A genuine template error is surfaced
- **GIVEN** a template that raises regardless of its data
- **WHEN** the report is built with parallelism enabled
- **THEN** discovery stops after a wave that raises without discovering a new unit, and the error from the real render is surfaced to the caller

### Requirement: Degraded parallel runs are reported

The library SHALL log a WARNING naming the cause and the number of live fetches whenever a
parallel run is not fully accelerated — discovery stopped at the wave cap, or the real render
fetched any unit live. A degraded run SHALL NOT fail the report.

#### Scenario: Live fetches during the real render are reported
- **WHEN** the real render fetches one or more units live
- **THEN** a WARNING is logged stating how many units were fetched live, and the report is produced

#### Scenario: A fully accelerated run logs no degradation warning
- **WHEN** every unit the real render requests is served from the cache
- **THEN** no degradation WARNING is logged

### Requirement: Per-source concurrency limit

The library SHALL accept an optional `prewarm_max_per_source` integer; when set, no more than that
many pre-warm fetches SHALL run concurrently against the same data source, while the total stays
bounded by `parallelism`. When unset, the only limit SHALL be `parallelism`.

#### Scenario: One endpoint is throttled while others proceed
- **GIVEN** `parallelism` `8`, `prewarm_max_per_source` `2`, and a wave with six units on endpoint A and two on endpoint B
- **WHEN** the wave is pre-warmed
- **THEN** at no moment are more than two fetches against endpoint A in flight, and the fetches against endpoint B are not blocked by A's limit

#### Scenario: No per-source limit by default
- **GIVEN** `prewarm_max_per_source` unset and `parallelism` `8`
- **WHEN** a wave with eight units on one endpoint is pre-warmed
- **THEN** up to eight fetches against that endpoint run concurrently

### Requirement: Parallel run summary

At the end of every parallel run, successful or aborted, the library SHALL log one INFO record
summarising the run: waves run, units pre-warmed, cache hits, live fetches, the abort reason if
any, and the slowest pre-warmed units with their durations.

#### Scenario: Summary after a successful run
- **WHEN** a parallel run completes
- **THEN** one INFO record reports waves run, units pre-warmed, cache hits, live fetches and the slowest units

#### Scenario: Summary after an aborted run
- **WHEN** a parallel run is aborted by a failing pre-warm fetch
- **THEN** the summary record is still logged and names the abort reason
