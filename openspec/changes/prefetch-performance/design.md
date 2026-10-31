<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: EPIC `prefetch-performance` ([proposal.md](proposal.md)); modifies capabilities
> `parallel-report-executor` and `batch-document-rendering`.

## Context

`ReportBuilder` (`eds4jinja2/services/report_builder.py`, 2.1.1) fetches data in two ways:

- **`parallelism` unset or 1**: templates call the real data-source builders; every `fetch_*` runs.
- **`parallelism` > 1**: `__with_prefetch(parallelism, env, variables, render)` wraps the builders
  in `env.globals` with `wrap_builders(..., FetchCoordinator())`, renders once in `Phase.RECORD`
  (each `fetch_*` registers a key and returns an empty placeholder), runs `coordinator.prewarm()`
  (all registered fetches on a thread pool, all-or-nothing), then calls `render()` in
  `Phase.RENDER` (cache hits served, misses run live and are not stored). A record-pass exception
  restores the unwrapped globals and calls `render()` without any cache.

A batch (`__render_batch`) calls `__render_text` per output, so each output gets its own
coordinator, record pass, pre-warm and cleanup. The cache, `FetchCache`, pickles each `(content,
error)` result to `<tempdir>/<sha256 key>.pickle` and unpickles it on every read.

Cache keys are `sha256(repr((source_id, query_repr, method)))`, where `source_id` is the builder name
with its arguments and `query_repr` is the `with_query` / `with_query_from_file` / `with_uri` call.
They do not depend on the output being rendered, so one coordinator can serve a whole batch.

## Goals / Non-Goals

**Goals:** DEC-1 to DEC-6 of the [EPIC](proposal.md#key-decisions). **Non-Goals:** the EPIC's
[no-gos](proposal.md#no-gos).

## Decisions

- **P-1 One fetch step for every render.** `__with_prefetch` becomes
  `__with_fetching(env, record_variables: Sequence[Mapping[str, Any]], render: Callable[[], T]) -> T`.
  It always creates one `FetchCoordinator` and wraps the data-source builders, also with `parallelism`
  1 (that is what memoises, DEC-3):
  - `parallelism` > 1: record pass once per entry of `record_variables`, one `prewarm`, then
    `render()` in `Phase.RENDER`;
  - `parallelism` 1: straight to `Phase.RENDER` and `render()` — no record pass, no thread pool.

  `make_document()` calls it with `[{}]` and `__render_to_output`; a batch calls it once with
  `list(outputs.values())` and a `render` that returns `{name: text}` for every output (DEC-1, item 1
  of the outline). `__render_text` goes away.
- **P-2 A record-pass failure no longer abandons the coordinator.** When the record pass of one entry
  raises, the warning `Parallel record pass failed (%s); its uncached fetches run live` is logged, the
  entry is skipped, and the next entry is recorded. Whatever was registered before the failure is
  pre-warmed with the rest. In `Phase.RENDER` that output's unrecorded fetches are cache misses: they
  run live and are memoised. Rejected: today's restore-globals-and-render-uncached fallback, which
  would throw away the batch's cache for every later output.
- **P-3 Memoise cache misses (DEC-3, DEC-5).** In `Phase.RENDER`, `FetchCoordinator.fetch` stores a
  live result whose `error` is `None` under its key; a result with an error is returned but not
  stored, so the next identical call runs again.
- **P-4 Two caches, one interface (DEC-2).** `parallel_executor` gets `MemoryFetchCache` (a `dict`;
  `get` returns `copy.deepcopy(value)`, DEC-4; `cleanup` clears it). The existing pickle cache is
  renamed `DiskFetchCache` (unchanged behaviour; unpickling already returns a fresh object). It is
  not exported from `eds4jinja2`; only `tests/unit/services/test_parallel_executor.py` imports it. Both
  offer `has`, `get`, `put`, `cleanup`. `FetchCoordinator()` defaults to `MemoryFetchCache()`.
- **P-5 Configuration.** New key `prefetch_cache` in `config.json` (constant `PREFETCH_CACHE`), with
  values from `enum CacheMedium {MEMORY = "memory", DISK = "disk"}`, default `memory`. It is read and
  validated in `ReportBuilder.__init__`: an unknown value raises `ValueError` naming the key and the
  allowed values, so a bad configuration fails before any listener, render or fetch. The setting
  applies with any `parallelism` (one rule; the sequential memo uses the same cache).
- **P-6 Benchmark (DEC-6).** `scripts/benchmark_prefetch.py`, run with `make benchmark`, not part of
  `make check-all`. It builds a template package in a temp folder and injects `from_endpoint` as a
  fake data source that sleeps 50 ms per `fetch_tabular` and counts calls. It prints wall time and
  fetch count for each scenario of the worked example below. It runs against whatever eds4jinja2 is
  installed, so "before" is measured on `master` and "after" on the branch; both tables go in the PR.

## Algorithm / approach

```text
__with_fetching(env, record_variables, render):
    coordinator = FetchCoordinator(new cache per prefetch_cache)
    original = dict(env.globals); wrap data-source builders in env.globals
    try:
        if parallelism > 1:
            coordinator.set_phase(RECORD)
            for variables in record_variables:
                try:   env.get_template(template).render(**variables)
                except Exception as e: log warning; continue          # P-2
            coordinator.prewarm(parallelism)                          # all-or-nothing, as today
        coordinator.set_phase(RENDER)
        return render()                                               # hits copied out, misses run live + memoised
    finally:
        coordinator.cleanup(); restore env.globals
```

Idempotency: a render or batch has no side effect on the data sources (fetches are reads); re-running
it repeats the fetches. Nothing is cached between calls (no-go), so a retry always sees fresh data.

### Worked example (the benchmark's scenarios)

A template with 5 queries: 2 identical in every output, 3 that depend on the output's variable `g`.
A batch of 20 outputs, each fetch sleeping 50 ms.

| Scenario | 2.1.1 fetches | 2.1.1 time (approx.) | 2.2.0 fetches | 2.2.0 time (approx.) |
|---|---|---|---|---|
| `parallelism` 8, batch of 20 | 100 (5 per output) | 20 pre-warms × 50 ms ≈ 1.0 s | 62 (2 shared + 60) | ⌈62 / 8⌉ = 8 rounds × 50 ms ≈ 0.4 s |
| `parallelism` 1, batch of 20 | 100 | 100 × 50 ms ≈ 5.0 s | 62 | 62 × 50 ms ≈ 3.1 s |
| `parallelism` 1, one report repeating one query 3 times | 3 | ≈ 150 ms | 1 | ≈ 50 ms |
| `parallelism` 8, 20 outputs on an in-memory rdflib graph, cache `disk` vs `memory` | — | disk round-trip per read | — | memory ≤ disk |

Acceptance (recorded in the PR, not asserted in CI): the parallel batch at least 2× faster than
2.1.1; the fetch counts exactly as in the table; the memory cache not slower than the disk cache.

### Anti-patterns

| Don't | Do instead | Why |
|---|---|---|
| hand out the stored DataFrame itself | `copy.deepcopy` on every `get` | a helper that edits in place (`simplify_uri_columns_in_tabular`) would change the result for every later use (DEC-4) |
| store a result whose `error` is set | return it, store nothing | one transient failure would repeat for the rest of the render (DEC-5) |
| one coordinator per output in a batch | one per batch | shared fetches would run once per output again (DEC-1) |
| restore the unwrapped globals after a record-pass failure | skip that entry, keep recording | the batch would lose its cache and memo for later outputs (P-2) |
| keep a cache across calls (on the builder) | a new coordinator per render or batch | data could be stale; nothing outlives one call (no-go) |
| assert timings in the test suite | assert fetch counts; time in the benchmark | shared CI runners make timings flaky (DEC-6) |
| write to the cache from pre-warm worker threads | `put` after `run_parallel` returns, on the calling thread | single writer, no lock needed (as today) |

## Error matrix

| Failure mode | How it is detected | Expected handling |
|---|---|---|
| `prefetch_cache` has an unknown value | `CacheMedium(value)` raises in `__init__` | `ValueError` naming `prefetch_cache` and `memory`, `disk`; nothing rendered or fetched |
| record pass of one output raises | exception in the record loop | warning logged; that output's recorded fetches are pre-warmed, the rest run live and are memoised; other outputs unaffected (P-2) |
| a pre-warm fetch fails | `error` set in `prewarm` | `RuntimeError` (all-or-nothing), whole render or batch aborts, cache cleaned up — as in 2.1 |
| a live fetch fails during render | `error` set in `fetch` | `(None, error)` returned to the template (fail-safe, as today), not stored; the next identical call retries (DEC-5) |
| template raises during the real render | exception from `render()` | propagates; cache cleaned up, globals restored (`finally`) |
| a disk-cache write fails (disk full) | `OSError` from `DiskFetchCache.put` | propagates; temp folder removed in `finally` — as in 2.1 |
| results exceed memory | the process runs out of memory | not handled; documented: set `"prefetch_cache": "disk"` (DEC-2) |
| two different sources produce one key | — | cannot happen with value-based `repr`; an object without one gets an identity `repr`, which only causes a miss (EPIC rabbit-hole) |

## Test cases

Fetch counts use a counting fake source injected as `from_endpoint` (as in
`tests/unit/services/test_report_builder_render_documents.py`).

| What | Test (to write) |
|---|---|
| a query shared by 3 outputs runs once, `parallelism` 4 | `test_parallel_batch_fetches_shared_query_once` |
| a query shared by 2 outputs runs once, `parallelism` 1 | `test_sequential_batch_fetches_shared_query_once` |
| a query repeated 3 times in one report runs once, `parallelism` 1 | `test_sequential_report_memoises_repeated_query` |
| editing a fetched DataFrame in place does not change the next use | `test_memoised_result_is_a_copy` |
| a failing fetch is retried on its next call | `test_failed_fetch_is_not_memoised` |
| one output's record pass fails; the others are still pre-warmed once | `test_record_failure_keeps_batch_prefetch` (replaces the 2.1 fallback test) |
| default cache creates no temp folder; `disk` creates one and removes it | `test_memory_cache_by_default`, `test_disk_cache_opt_in_cleaned_up` |
| unknown `prefetch_cache` | `test_unknown_prefetch_cache_is_refused` |
| 2.1 tests (`make_document` parallel = sequential, batch parity, listeners) | unchanged, green |

## Risks / Trade-offs

- **Behaviour change on the default path (DEC-3)**: non-deterministic queries repeated in one render
  now return their first result. → Called out in the CHANGELOG and docs; minor version 2.2.0.
- **Behaviour change after a record-pass failure (P-2)**: in 2.1 the fallback rendered without any
  pre-warm, so a failing fetch reached the template as `(None, error)`. Now the fetches recorded
  before the failure are pre-warmed, and if one of them fails the run aborts (all-or-nothing). →
  Consistent with the rest of the parallel path; listed in the CHANGELOG.
- **Memory (DEC-2)**: a batch holds every output's results until it ends. → `"prefetch_cache": "disk"`.
- **Deep copies** of large DataFrames cost time on every read. → Still far cheaper than unpickling
  (which also copies) and than any query; the benchmark's in-memory scenario checks it.
- **Builders are now wrapped with `parallelism` 1.** A template or helper that type-checks a data
  source would see the `CachingDataSource` proxy; it forwards every other attribute (`__getattr__`),
  as the parallel path has since 1.x. → No known template does this; the full suite runs on it.
- **Not thread-safe**, as before: one batch at a time per builder.

## Open Questions

None.
