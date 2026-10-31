<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [ ]` checkboxes. -->

> Derives from: EPIC `parallel-executor-hardening` (`proposal.md`); design in `design.md`.
> Every task is TDD: write the failing test first, then the code. "Spec:" names the requirement /
> scenario in `specs/parallel-report-executor/spec.md` the task proves.

## 1. Per-source dispatch in `run_parallel` (P-2)

- [ ] 1.1 In `tests/unit/services/test_parallel_executor.py`, add a failing test: 6 thunks in group A
  and 2 in group B, `max_workers=8`, `max_per_group=2`; thunks block on a `threading.Event` and
  record in-flight counts per group; assert max in-flight A ≤ 2 and both B thunks start while A is
  still saturated; results stay in input order. Spec: *Per-source concurrency limit → One endpoint
  is throttled while others proceed*.
- [ ] 1.2 Add a failing test: with `max_per_group=None`, 8 thunks of one group reach 8 in flight.
  Spec: *→ No per-source limit by default*.
- [ ] 1.3 Implement `run_parallel(thunks, max_workers, group_of=None, max_per_group=None)` in
  `eds4jinja2/services/parallel_executor.py` with the dispatcher (`wait(FIRST_COMPLETED)`);
  existing callers and the all-or-nothing test (`test_run_parallel_all_or_nothing_reraises`) stay
  green.

## 2. Waves, stats and record-error tolerance in `FetchCoordinator` (P-1, P-3, P-4, P-5)

- [ ] 2.1 Add `RunStats` dataclass and constants `PREWARM_MAX_WAVES` / `DEFAULT_MAX_WAVES = 5` /
  `PREWARM_MAX_PER_SOURCE` in `parallel_executor.py`; store `source_id` and a label in the registry.
- [ ] 2.2 Failing test (fake render callable that fetches unit X, then unit Y only if X's result is
  non-empty): `discover` pre-warms X in wave 1, Y in wave 2, stops after wave 3 with nothing new;
  `stats.waves == 3`, `prewarmed == 2`. Spec: *Discovery proceeds in waves → A data-dependent query
  is pre-warmed in the second wave*; *→ Discovery stops when nothing new is found*.
- [ ] 2.3 Failing test: three dependency levels with `max_waves=2` → two waves, `capped is True`,
  level-3 unit absent from the cache. Spec: *→ Discovery stops at the wave cap*.
- [ ] 2.4 Failing test: render raises when X's result is empty → wave 1 still pre-warms X; wave 2
  completes. A render that always raises and discovers nothing new stops discovery without
  raising from `discover`. Spec: *A record-pass error does not abandon parallelism* (both
  scenarios, coordinator half).
- [ ] 2.5 Failing test: in `RENDER`, hits and misses increment `cache_hits` / `live_fetches`;
  `durations` holds one entry per pre-warmed unit.
- [ ] 2.6 Failing tests for the coordinator rows of `design.md` *Edge cases*: no fetch at all
  (`waves=1 prewarmed=0`); the same query twice in one wave (fetched once); a wave-2 fetch failure
  raises from `discover` and no wave 3 runs; label truncated to 120 characters for a long query
  and for a `rdflib.Graph` first argument.
- [ ] 2.7 Implement `FetchCoordinator.discover(render, max_waves, max_workers, max_per_source)`,
  `prewarm(keys, max_workers, max_per_source)` (P-9) and the stats per `design.md` *Algorithm*;
  `prewarm` passes `group_of=source_id` to `run_parallel`; update existing call sites of
  `prewarm(max_workers)` in `tests/unit/services/test_parallel_executor.py`.

## 3. `ReportBuilder` orchestration (P-6, P-7, P-8)

- [ ] 3.1 In `tests/unit/services/test_report_builder_parallel.py`, add failing tests with an
  in-memory graph and a two-level template (list query, then one query per row, plus `iloc[0]` on
  the list): output equals the sequential render; no live fetch; no degradation WARNING
  (`caplog`). Spec: *A record-pass error does not abandon parallelism → A placeholder-induced error
  is overcome by real data*; *Degraded parallel runs are reported → A fully accelerated run logs no
  degradation warning*.
- [ ] 3.2 Failing test: same template with `prewarm_max_waves: 1` → output equals sequential;
  WARNING mentions the wave cap and the live-fetch count. Spec: *Degraded parallel runs are
  reported → Live fetches during the real render are reported*.
- [ ] 3.3 Failing test: a template that raises regardless of data → `make_document` raises the
  template error (not a silent sequential render). Spec: *→ A genuine template error is surfaced*.
- [ ] 3.4 Failing tests: one INFO summary record after a successful run, and after a run aborted by
  a failing fetch (record names the abort reason). Spec: *Parallel run summary* (both scenarios).
- [ ] 3.5 Failing tests: `prewarm_max_waves` of `0`, `-1`, `"5"`, `True` and
  `prewarm_max_per_source` of `0`, `True` raise `ValueError` naming the key, before any fetch and
  without creating a temp folder (P-6).
- [ ] 3.6 Failing test: wave 1 succeeds and a wave-2 fetch fails → `make_document` raises, no output
  file, no temp folder left (`design.md` *Edge cases*).
- [ ] 3.7 Implement in `eds4jinja2/services/report_builder.py`: validation (P-6), remove the
  record-failure sequential fallback (P-7), call `coordinator.discover`, the log records of P-10,
  summary in `finally` (P-8). Existing parallel tests (`test_parallel_and_sequential_outputs_match`,
  `test_no_prewarm_temp_dirs_leak`) and the sequential-default tests stay green.

## 4. Docs, version, gate

- [ ] 4.1 Update `docs/modules/ROOT/pages/parallel-execution.adoc`: waves, the two new config keys
  with defaults, degraded-run WARNING, the run summary, re-render cost and template side effects;
  remove any `prefetch` manifest mention. Add the keys to the table in `templating.adoc`.
- [ ] 4.2 Bump `eds4jinja2/VERSION` and the static copy in `pyproject.toml` 2.0.0 → 2.1.0 (MINOR,
  additive config); `make check-version` passes.
- [ ] 4.3 Run `make check-all` (lint, typecheck, architecture, `openspec validate --strict`, tests)
  green.

## Roadmap

- [ ] 1.1 · [ ] 1.2 · [ ] 1.3 · [ ] 2.1 · [ ] 2.2 · [ ] 2.3 · [ ] 2.4 · [ ] 2.5 · [ ] 2.6 · [ ] 2.7 ·
  [ ] 3.1 · [ ] 3.2 · [ ] 3.3 · [ ] 3.4 · [ ] 3.5 · [ ] 3.6 · [ ] 3.7 · [ ] 4.1 · [ ] 4.2 · [ ] 4.3

## Verification

`make check-all` green; every scenario in `specs/parallel-report-executor/spec.md` has a named test
above; parallel output equals sequential output in every new `ReportBuilder` test; clarity gate
scores this PLAN ≥ 9/10.
