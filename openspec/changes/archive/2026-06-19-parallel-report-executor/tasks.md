<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [x]` checkboxes. -->

> Derived from EPIC `parallel-report-executor` (proposal.md)  <!-- cite your parent (golden thread) -->

## 1. SPARQLClientPool thread-safety fix (prerequisite, TDD: tests first)

- [x] 1.1 Write a failing concurrency regression test `tests/unit/test_remote_sparql_ds_concurrency.py`: N threads query the same endpoint URL with DISTINCT queries; assert each thread's `_fetch_*` sees its own query string and result (no clobbering)
- [x] 1.2 Implement the fix in `eds4jinja2/adapters/remote_sparql_ds.py` — `SPARQLClientPool` no longer hands out one shared mutable `SPARQLWrapper`; give each fetch isolated query state (fresh wrapper per call or per-thread via `threading.local`), keeping connection reuse only where safe; preserve `with_query`/`_fetch_*`/`__str__` signatures and the `(result, error)` contract; make the test pass

## 2. Executor port (TDD)

- [x] 2.1 Write failing unit tests `tests/unit/test_executor.py`: `ThreadPoolExecutorAdapter.map(fn, items, max_workers=N)` runs items concurrently and returns results in input order
- [x] 2.2 Add a failing test asserting ALL-OR-NOTHING: if any item's `fn` raises, `map` raises (first exception) after ALL_COMPLETED, surfacing the error
- [x] 2.3 Implement `eds4jinja2/builders/executor.py` — `Executor` protocol (`map(fn, items, *, max_workers)`) and `ThreadPoolExecutorAdapter` wrapping `concurrent.futures.ThreadPoolExecutor`; documented seam for a future process/Celery adapter (NOT implemented); make tests pass

## 3. Prefetch cache + cache-aware data sources (TDD)

- [x] 3.1 Write failing tests `tests/unit/test_prefetch.py`: `PrefetchUnit.key` equals `sha256(source_identity + "\n" + normalised_query)`; two units with the same `(source, query)` produce the same key (memoisation precondition)
- [x] 3.2 Add failing tests for `PrefetchContext`: `RECORD` mode registers a unit and returns an empty placeholder without executing; `register` dedupes by key (identical source+query registered once)
- [x] 3.3 Add failing tests for `SERVE` mode: a staged result for a key is served from the temp folder; a cache MISS falls back to a LIVE fetch returning the real result
- [x] 3.4 Add failing tests for `cleanup()`: the temp folder is removed; cleanup is idempotent
- [x] 3.5 Implement `eds4jinja2/builders/prefetch.py` — `PrefetchMode` enum (`RECORD`/`SERVE`/`LIVE`), `PrefetchUnit` (key, execute, stage/read under `temp_dir/key`), `PrefetchContext` (mode, register/units/fetch_unit/seed_from_manifest/cleanup); config-key and manifest-field constants; make tests pass
- [x] 3.6 Make the `from_endpoint` (and `from_memory`, if present) builders in `eds4jinja2/builders/jinja_builder.py` cache-aware via the active `PrefetchContext` (RECORD→register+placeholder, SERVE→serve-or-live, no context→today's direct fetch); add tests asserting all three modes; preserve the `(result, error)` fail-safe contract

## 4. ReportBuilder pre-warm orchestration (TDD)

- [x] 4.1 Write a failing backward-compat test in `tests/unit/test_report_builder.py`: with `parallelism` unset (or `1`), `make_document` takes the existing `template.stream().dump(...)` path — no record pass, no executor call, NO temp folder created, output unchanged
- [x] 4.2 Write a failing test: with `parallelism=N>1`, the (injected fake) executor is called with all discovered units and `max_workers=N`, fetches run before the render, and the render serves cached results
- [x] 4.3 Write a failing all-or-nothing test: one pre-warm unit raises → `make_document` aborts, NO output file is written, the error propagates
- [x] 4.4 Write failing cleanup tests: the temp folder is removed after a successful run AND after an aborted run (try/finally)
- [x] 4.5 Write a failing test: a query NOT discovered in the record pass (data-dependent) runs LIVE during the render (graceful fallback, no crash)
- [x] 4.6 Implement the orchestration in `eds4jinja2/builders/report_builder.py` — read `parallelism` (default 1); `parallelism<=1` keeps the unchanged sequential path; otherwise RECORD render → seed manifest → `executor.map(...)` all-or-nothing → SERVE render → `finally: cleanup`; inject the default `ThreadPoolExecutorAdapter` (overridable for tests); make tests pass

## 5. Manifest, config keys, parity

- [x] 5.1 Write a failing test that an explicit `prefetch` manifest in `config.json` seeds units deterministically, and a malformed entry (missing `source`/`query`) is rejected with a clear error before any fetch
- [x] 5.2 Write a parity test: render the same report with `parallelism=1` and `parallelism=N>1` and assert byte-identical output
- [x] 5.3 Wire the config-key constants (`CONFIG_PARALLELISM`, `CONFIG_PREFETCH`, `CONFIG_PREFETCH_TEMP_DIR`, `PREFETCH_SOURCE`, `PREFETCH_QUERY`); default temp dir via `tempfile.mkdtemp`; make tests pass

## 6. Versioning, docs, guardrails

- [x] 6.1 Bump `eds4jinja2/__init__.py` `__version__` 0.3.1 → 0.4.0 (MINOR)
- [x] 6.2 Add a changelog/README note: the `parallelism` config key, the optional `prefetch` manifest, all-or-nothing semantics, threads-only model, and that templates are unchanged and the default is sequential
- [x] 6.3 Run `make` checks: import-linter (executor/prefetch in `builders`, adapters stay innermost; no upward imports), ruff, mypy, tox (py311/py312) green; confirm ≥80% coverage on new code

## Roadmap

- [x] 1.1 · [ ] 1.2 · [ ] 2.1 · [ ] 2.2 · [ ] 2.3 · [ ] 3.1 · [ ] 3.2 · [ ] 3.3 · [ ] 3.4 · [ ] 3.5 · [ ] 3.6 · [ ] 4.1 · [ ] 4.2 · [ ] 4.3 · [ ] 4.4 · [ ] 4.5 · [ ] 4.6 · [ ] 5.1 · [ ] 5.2 · [ ] 5.3 · [ ] 6.1 · [ ] 6.2 · [ ] 6.3

## Verification

All unit + concurrency + parity tests green under tox (py311/py312); import-linter/ruff/mypy clean;
the backward-compat test proves a no-`parallelism` `ReportBuilder` is byte-for-byte unchanged (no
record pass, no temp folder, no executor); the all-or-nothing test proves no output file is produced
on a pre-warm failure; the cleanup tests prove the temp folder is removed on success and on failure;
the concurrency test proves same-endpoint queries do not clobber each other; templates remain
byte-for-byte unchanged; clarity gate scores the PLAN ≥9/10.
