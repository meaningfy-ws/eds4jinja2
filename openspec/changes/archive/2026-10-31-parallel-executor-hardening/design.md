<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: EPIC `parallel-executor-hardening` (`proposal.md`); modifies capability
> `parallel-report-executor`.

## Context

Today (`eds4jinja2/services/parallel_executor.py`, `report_builder.py::__make_document_parallel`):

- `FetchCoordinator` has two phases. In `RECORD` every `fetch_*` registers `(real_ds, method)` under
  a sha256 key and returns an empty placeholder. In `RENDER` it serves from `FetchCache`, or
  fetches live on a miss.
- `__make_document_parallel` does **one** record pass. If that pass raises, it restores the globals
  and renders the whole report sequentially, logging one WARNING.
- `prewarm(max_workers)` runs every registered unit through `run_parallel` (ThreadPoolExecutor,
  all-or-nothing) and stages `(content, error)` in the cache; a non-`None` `error` aborts.
- The cache key is `sha256(repr((source_id, query_repr, method)))`, where
  `source_id = (builder_name, args, sorted_kwargs)`, e.g. `("from_endpoint", ("http://x/sparql",), ())`.
- Nothing counts hits or live fetches, and nothing limits concurrency per source.

Constraints: everything stays in `services` (import-linter); no new runtime dependency (EPIC
no-gos); `parallelism` unset/`1` never reaches this code (DEC-7); all-or-nothing per wave (DEC-3).

## Goals / Non-Goals

**Goals:** discovery in waves (DEC-1, DEC-2, DEC-8); record-pass errors tolerated; degraded runs
reported; per-source limit (DEC-9); one summary record per run (DEC-6); spec drops the manifest
(DEC-4).

**Non-Goals:** everything under the EPIC's *No-gos*; any change to `FetchCache`, `CachingDataSource`,
`wrap_builders`, the adapters or the sequential path.

## Decisions

New choices made while planning (EPIC decisions are cited, not repeated):

- **P-1 — the wave loop lives in `FetchCoordinator.discover(render, ...)`**, not in
  `ReportBuilder`. The builder passes a zero-argument `render` callable
  (`lambda: template.render()`); the coordinator owns phases, cache and stats. Keeps
  `report_builder.py` a thin orchestrator and the loop unit-testable without templates.
  *Rejected:* loop in `ReportBuilder` (needs a template to test every branch).
- **P-2 — per-source limit by dispatch, not by blocking.** `run_parallel` gains an optional
  `group_of` (thunk index → group key) and `max_per_group`. A dispatcher submits a thunk only when
  its group has a free slot and the pool has a free worker, waiting with
  `concurrent.futures.wait(..., FIRST_COMPLETED)`. *Rejected:* a `threading.Semaphore` per source
  acquired inside the thunk — blocked thunks hold pool workers, so a large source starves the
  others (violates the "B not blocked by A" scenario).
- **P-3 — the group key is `source_id`** (already computed by `wrap_builders`); the registry
  stores it alongside `(real_ds, method)`. No URL normalisation (EPIC rabbit-hole).
- **P-4 — the stats are a `RunStats` dataclass** owned by the coordinator: `waves`,
  `prewarmed`, `cache_hits`, `live_fetches`, `capped`, `abort_reason`, `durations`
  (`key → (label, seconds)`). The thunk times itself with `time.perf_counter` and returns
  `(result, seconds)`, so stats are written only on the calling thread (no locks).
- **P-5 — a unit's label** for the summary is `f"{builder_name}({first_arg!r}) {query}"` built
  from `source_id` and the first positional argument of `query_repr`, whitespace-collapsed and
  truncated to 120 characters. Human-only; never used as a key.
- **P-6 — config validation at the start of `__make_document_parallel`**, before any record pass:
  `prewarm_max_waves` must be an `int` (not `bool`) ≥ 1, default `5`; `prewarm_max_per_source`
  must be absent/`None` or an `int` (not `bool`) ≥ 1. Anything else raises
  `ValueError(f"{key} must be an integer >= 1, got {value!r}")`. The keys are module constants next
  to `PARALLELISM` (no free strings).
- **P-9 — `prewarm` takes the units to fetch.** Signature becomes
  `prewarm(keys, max_workers, max_per_source)`; `discover` passes the wave's pending keys only.
  `_registry` keeps every unit seen (`key → (real_ds, method, source_id, label)`); a unit is
  *pending* if it is in `_registry` but not in the cache.
- **P-10 — exact log records** (module logger `eds4jinja2.services.report_builder`):

  | Level | When | Message format |
  |---|---|---|
  | INFO | every parallel run, in `finally` | `"Parallel run: waves=%d prewarmed=%d cache_hits=%d live=%d aborted=%s slowest=%s"` — `aborted` is `abort_reason` or `None`; `slowest` is the top 5 `(label, seconds rounded to 2)` by duration, descending |
  | WARNING | after a successful real render, if `capped` | `"Parallel run degraded: stopped at wave cap (%d); %d unit(s) fetched live"` |
  | WARNING | after a successful real render, if not `capped` and `live_fetches > 0` | `"Parallel run degraded: %d unit(s) fetched live during render"` |

  Tests assert on the record's level and on substrings `"wave cap"`, `"fetched live"`,
  `"waves="`, `"aborted="`, never on full strings.
- **P-7 — the old record-failure fallback is removed.** A record-pass error now continues
  discovery (spec: *A record-pass error does not abandon parallelism*); the
  `__restore_globals` + sequential re-render branch goes away. The `finally` that restores globals
  and cleans up stays.
- **P-8 — the summary is logged in `ReportBuilder`'s `finally`** via `coordinator.stats`, so it is
  emitted on success and on abort alike. One INFO record; the degradation WARNING is a separate
  record logged after a successful real render.

## Algorithm / approach

```
discover(render, max_waves, max_workers, max_per_source):
    phase = RECORD
    for wave in 1..max_waves:
        stats.waves = wave
        pending = {}                        # units first seen in this wave
        try: render()                       # fetch(): cache hit → real result
        except Exception: errored = True    #          known/pending → placeholder
        else: errored = False               #          unknown → add to pending, placeholder
        if not pending: break               # converged (errored or not)
        prewarm(pending, max_workers, max_per_source)   # all-or-nothing (DEC-3)
        if wave == max_waves: stats.capped = True
    phase = RENDER
```

`fetch()` in `RENDER`: cache hit → `stats.cache_hits += 1`; miss → `stats.live_fetches += 1`, live
fetch. A unit pre-warmed in an earlier wave is never re-recorded as pending (it is a cache hit).

`ReportBuilder.__make_document_parallel`:
```
validate config (P-6); coordinator = FetchCoordinator(); wrap builders
try:
    coordinator.discover(lambda: template.render(), max_waves, parallelism, max_per_source)
    __render_to_output()
    if stats.capped or stats.live_fetches: logger.warning(<cause>, <live count>)
except Exception as e: stats.abort_reason = repr(e); raise
finally: logger.info(<summary>); coordinator.cleanup(); restore globals
```

**Worked example** — template:
```
{% set cats, _ = from_endpoint(E).with_query(Q_CATS).fetch_tabular() %}
{{ cats.iloc[0]['label'] }}
{% for c in cats['uri'] %}
  {% set n, _ = from_endpoint(E).with_query("SELECT ... <" ~ c ~ ">").fetch_tabular() %}{{ n|length }}
{% endfor %}
```
Data: `Q_CATS` returns 3 categories.

| Wave | `cats` in record pass | Render outcome | Pending | Action |
|---|---|---|---|---|
| 1 | placeholder (empty DataFrame) | raises on `iloc[0]` | `{Q_CATS}` | pre-warm 1 unit |
| 2 | real (3 rows) | completes | 3 per-category queries | pre-warm 3 units in parallel |
| 3 | real | completes | `{}` | stop |

Real render: 4 cache hits, 0 live fetches, no WARNING. Summary:
`parallel run: waves=3 prewarmed=4 cache_hits=4 live=0 slowest=[...]`.
With `prewarm_max_waves: 1`: wave 1 pre-warms `Q_CATS`, `capped=True`; the real render
fetches the 3 per-category queries live → WARNING `"... stopped at wave cap (1); 3 units fetched
live"`.

**Per-source dispatch example** (P-2): `parallelism=8`, `max_per_source=2`, units A1..A6 on source
A and B1, B2 on source B. Dispatcher submits A1, A2, B1, B2 (A is full at 2); each completed A
frees one A slot → next A submitted. In-flight A never exceeds 2; B starts immediately.

**Idempotency:** every unit is a read-only query; a wave re-render re-executes no query already in
the cache (it is a hit). An aborted run leaves nothing behind (temp folder removed in `finally`), so
re-running the whole report is safe. There is no retry (DEC-3).

### Anti-patterns
| Don't | Do instead | Why |
|---|---|---|
| Acquire a per-source semaphore inside the thunk | Dispatch only when a slot is free (P-2) | Blocked workers starve other sources |
| Return fake rows from placeholders | Empty placeholder + next wave with real data (DEC-2) | Fake data drives wrong branches and records phantom queries |
| Swallow the record-pass exception after the last wave | Let the real render surface it | Hides genuine template bugs |
| Mutate `RunStats` from worker threads | Return timings with the result; update on the caller thread (P-4) | No locks needed |
| Key the per-source limit on a normalised URL | Use `source_id` as is (P-3) | Rabbit-hole; `source_id` already identifies the source |
| Fall back to a full sequential render on record error | Continue waves (P-7) | That fallback is the silent degradation this EPIC removes |

## Error matrix

There is no user-facing UI; the "user" is the `make_document` caller (library or `mkreport`),
who sees an exception or a log record (P-10). No retries anywhere (DEC-3).

| Failure mode | How it is detected | Expected handling | Log |
|---|---|---|---|
| Record pass raises on a placeholder | `except Exception` around `render()` in `discover` | Pre-warm the units recorded so far; next wave | DEBUG (exception repr) |
| Record pass raises, no new unit | `errored and not pending` | Stop discovery; the real render raises → `abort_reason` set, error propagates | INFO summary |
| Pre-warm fetch returns `error` / raises (any wave) | `prewarm` result check / `run_parallel` re-raise | Abort the report (DEC-3), no later wave runs; temp folder removed | INFO summary with `aborted=` |
| Wave cap reached while still discovering | `wave == max_waves` with non-empty pending | `capped=True`; remaining dependents fetched live | WARNING (P-10) |
| Real render fetches live | cache miss in `RENDER` | `live_fetches += 1`; report produced | WARNING (P-10) |
| Non-deterministic queries (never converge) | Same as wave cap | Same as wave cap | WARNING |
| Invalid `prewarm_max_waves` / `prewarm_max_per_source` | P-6 validation | `ValueError` (P-6 text), before any fetch, no temp folder | none |
| Real render raises mid-stream | Exception from `__render_to_output` | Same as sequential mode today (a partial output file may remain); cleanup in `finally` | INFO summary with `aborted=` |

### Edge cases (each gets a test in `tasks.md`)

| Case | Expected |
|---|---|
| Template with no `fetch_*` | wave 1 has no pending → `waves=1 prewarmed=0`; render identical to sequential |
| The same query twice in one wave | one pending unit (key dedupe), fetched once, two cache hits |
| `prewarm_max_waves: 1` | single record pass, i.e. today's behaviour plus stats and warning |
| Wave 1 succeeds, a wave-2 fetch fails | abort; wave-1 results discarded with the temp folder; no output file |
| `prewarm_max_per_source` ≥ the number of units of every source | identical to unset |
| `True` / `"5"` / `0` as a config value | `ValueError` (P-6) |
| A `from_graph(<rdflib.Graph>)` source | label is the truncated `repr`; group key is `source_id` as is |

## Risks / Trade-offs

- [Each wave re-renders the template: CPU and template side effects × waves] → bounded by
  `prewarm_max_waves`; documented in `parallel-execution.adoc`.
- [Behaviour change: a record-pass error no longer degrades to a full sequential render] → the
  real render's output is identical either way (parity test); only speed and logging differ.
- [A template that loops over thousands of fetched rows produces thousands of units in one wave]
  → bounded by `parallelism` and `prewarm_max_per_source`; deduped by key.
- [The dispatcher is new concurrency code] → covered by a deterministic test using events/barriers
  that records the maximum in-flight count per group.

## Open Questions

None blocking. The EPIC's open questions were settled (proposal *Decision record*).
