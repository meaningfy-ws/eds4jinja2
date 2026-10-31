<!-- The EPIC — the shaped bet. In Meaningfy the EPIC *is* the OpenSpec proposal. -->

> **Closed unimplemented, 2026-10-31** (change `groom-living-specs`, DEC-3). 0 of 22 tasks were done;
> no consumer asks for waves, per-source limits or run stats; the design predates 2.1.0 (it targets
> `__make_document_parallel`, now `__with_prefetch`, and removes the record-pass fallback that
> `batch-document-rendering` requires). Its manifest cleanup (DEC-4) was done by
> `groom-living-specs`. Archived with `--skip-specs`: none of its spec deltas were merged. Re-shape
> as a new change if the need appears.

# EPIC: Parallel executor hardening — dependent fetches, honest fallback, polite concurrency

## Appetite

**MEDIUM.** Strengthens the one existing capability (`parallel-report-executor`): the record /
pre-warm loop becomes iterative, the fallback becomes visible, a per-endpoint limit is added, and
the spec is brought back in line with the code. Neighbours touched lightly (`report_builder.py`,
docs). No new execution backend, no template-syntax change, the sequential default untouched.

## Why

Parallelism already exists (`parallelism` in `config.json`, archived 2026-06-19), but it speeds up
only the *easy* case — independent queries whose arguments are known before any data arrives. The
slow reports we actually run are dominated by **data-dependent fetches**: a first query lists items,
and the template issues one query per item. In the record pass the first query returns an empty
placeholder, the loop never iterates, the inner queries are never discovered, and they all run
**live and sequentially** during the real render. Worse, templates that index into a result
(`df.iloc[0]`) crash the record pass, and the builder then silently renders the **whole** report
sequentially with only a log warning — the user believes the run is parallel when it is not.

Three smaller defects ride along: the spec promises a `prefetch` manifest that was never built
(spec ↔ code drift), nothing caps concurrent requests to a single endpoint (a high `parallelism`
can overload Fuseki or a public endpoint and turn a 429 into an all-or-nothing abort), and there is
no way to see what was pre-warmed versus fetched live.

## Solution outline

The outcome: **a report whose queries depend on earlier results is fetched in parallel, level by
level, and the user can see whether that happened.**

1. **Discovery in waves.** Replace the single record pass by a loop: record → pre-warm what was
   newly discovered → record again, now serving already-fetched units with **real data** and only
   unknown ones with placeholders. Each wave unlocks the next level of data-dependent queries
   (list → per-item queries → …). The loop stops when a wave discovers nothing new, or at a wave
   cap. Each wave's fetches run in parallel.
2. **A record-pass error is not the end of discovery.** If a wave's render raises, the units
   recorded *before* the error are still pre-warmed and the next wave retries with real data — a
   placeholder-induced error usually disappears once the data it indexed is real. Only an error in
   a wave that discovered nothing new is genuine; it is then surfaced by the real render, not
   swallowed.
3. **Honest fallback.** Whenever the builder renders with fewer accelerated fetches than it
   could (record pass abandoned, live misses during the real render), it says so loudly and
   specifically — not a single generic warning.
4. **Polite concurrency.** A per-endpoint concurrency limit on top of the global `parallelism`,
   so many endpoints can be queried widely while no single endpoint receives more than its share.
5. **A run summary.** At the end of a parallel run, one structured log record: waves run, units
   pre-warmed, cache hits, live misses, abort reason if any, slowest units.
6. **Spec ↔ code reconciled** for the `prefetch` manifest (see DEC-4).

Templates stay unchanged; everything remains behind `parallelism > 1`.

## Key decisions

<!-- Drafter's calls, accepted by the developer's "go ahead" (see Decision record). -->

- **DEC-1 (iterate the existing record pass, don't replace it)**: discovery becomes a bounded loop
  of record passes interleaved with parallel pre-warms, reusing `FetchCoordinator`, `FetchCache`
  and `run_parallel` as they are. *Rejected:* Jinja2 async mode (still sequential in document
  order), static analysis of the template AST (fails on variable-built queries), lazy futures
  (help only templates that fetch early).
- **DEC-2 (record passes serve cached real data)**: during a record pass a unit already in the
  cache returns its real result; only unknown units get a placeholder. This is what makes waves
  converge. *Rejected:* smarter placeholders (fake rows) — they would drive templates down wrong
  branches and record queries that never run in the real render.
- **DEC-3 (all-or-nothing still holds, per wave)**: any failed pre-warm fetch in any wave aborts
  the report, no output, error surfaced — the archived DEC-3 contract is unchanged.
- **DEC-4 (`prefetch` manifest is removed from the spec, not built)**: waves cover the
  data-dependent case the manifest was meant for; building it now would be speculative.
  *Rejected:* implementing the manifest (YAGNI; no consumer asks for it).
- **DEC-5 (per-endpoint limit keyed on source identity)**: the limit is applied per data source
  (endpoint URL, file path, graph), configured in `config.json`, defaulting to "no extra limit"
  so existing configs behave as today. *Rejected:* a global rate limiter / retry-with-backoff
  (retry contradicts all-or-nothing).
- **DEC-6 (observability through `logging` only)**: the run summary is a log record via the
  existing module logger. *Rejected:* metrics exporters, progress bars, a report file — new
  dependencies or surface for no named consumer.
- **DEC-7 (sequential default byte-for-byte unchanged)**: `parallelism` unset or `1` never enters
  any of this code — the archived DEC-4 contract is unchanged.

- **DEC-8 (wave cap)**: a new optional `prewarm_max_waves` key, default `5` (covers list → item →
  detail nesting with headroom). Reaching the cap is reported as a degraded run, never an error.
- **DEC-9 (per-endpoint limit shape)**: one number for all sources, `prewarm_max_per_source`,
  default unset = no limit beyond `parallelism`. *Rejected:* a per-URL map (no consumer needs it).
- **DEC-10 (no strict mode)**: degraded runs are reported loudly (outline item 3) but never fail
  the run. *Rejected:* an opt-in strict flag — added only when someone asks for it.
- **DEC-11 (no timing acceptance criterion)**: correctness is proven by output parity with the
  sequential render and by counting which fetches ran in which wave, not by wall-clock benchmarks
  (flaky in CI). A manual before/after timing on a real report is recommended, not gating.

## Decision record

Open questions 1–5 of the first draft were settled on 2026-10-30: the developer said "go ahead" on
the drafter's proposed defaults → DEC-4, DEC-8, DEC-9, DEC-10, DEC-11. These are the drafter's
calls, open to revision before the PLAN is derived.

## Rabbit-holes

- **Non-convergence.** A template whose queries depend on non-deterministic data (timestamps,
  random ordering) can discover "new" units forever — the wave cap is the guard; do not try to
  detect it more cleverly.
- **Side effects in templates** run once per wave. Document it; do not try to suppress them.
- **CPU cost of re-rendering.** Each wave re-renders the template. Acceptable for latency-bound
  reports; do not optimise rendering.
- **rdflib in-memory sources** stay GIL-bound — do not chase speed-up there.
- **Identifying "the endpoint"** for the per-endpoint limit: use the existing `source_id` from
  `wrap_builders`; do not normalise URLs.

## No-gos

- No change to the sequential default (`parallelism` unset or `1`).
- No parallel *rendering* of the template, no async rewrite, no process/Celery executor.
- No retry, backoff, partial output or resume — all-or-nothing stays.
- No template-syntax changes and no new template-facing API.
- No `prefetch` manifest implementation (DEC-4).
- No strict / fail-on-degradation mode (DEC-10).
- No new runtime dependency.
- No persistent cache across runs.

---

## What Changes

- `FetchCoordinator` / `ReportBuilder.__make_document_parallel`: single record pass replaced by a
  bounded wave loop; record passes serve cached real data; a record-pass error no longer abandons
  parallelism outright.
- Loud, specific reporting of degraded runs (abandoned discovery, live misses in the real render).
- Per-endpoint concurrency limit in the pre-warm, new optional `config.json` key(s).
- End-of-run summary log record.
- `parallel-report-executor` spec: manifest wording removed; new requirements for waves, error
  tolerance, visible degradation, per-endpoint limit, run summary.
- Docs: `parallel-execution.adoc` updated (waves, limits, summary, side effects).
- Version: MINOR bump (additive config, no breaking change).

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
- `parallel-report-executor`: discovery becomes iterative (waves) and tolerant of placeholder
  errors; degraded runs are visible; per-endpoint concurrency limit; run summary; the unimplemented
  `prefetch` manifest is removed from the requirements.

## Impact

- **Code**: `eds4jinja2/services/parallel_executor.py`, `eds4jinja2/services/report_builder.py`;
  tests under `tests/unit/services/`. Layering unchanged (all in `services`).
- **Config**: additive optional keys `prewarm_max_waves` (DEC-8) and `prewarm_max_per_source`
  (DEC-9).
- **Docs**: `docs/modules/ROOT/pages/parallel-execution.adoc`.
- **Golden thread**: modifies `openspec/specs/parallel-report-executor`; builds on the archived
  change `2026-06-19-parallel-report-executor` (DEC-3, DEC-4, DEC-7 there).
