<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [ ]` checkboxes. -->

> Derives from: EPIC `prefetch-performance` ([proposal.md](proposal.md)); design in [design.md](design.md).
> Every task is TDD: write the test named in design.md "Test cases" first, watch it fail, then code.
> "Spec:" names the requirement in [specs/](specs/) the task proves.

## 1. Caches

- [ ] 1.1 Add `MemoryFetchCache` (`get` returns a deep copy) and rename the pickle cache to
  `DiskFetchCache`, updating `tests/unit/services/test_parallel_executor.py` (P-4; Spec: The fetch
  cache is in memory by default and always cleaned up; Identical queries are fetched once — "A stored
  result is a copy")
- [ ] 1.2 `FetchCoordinator`: default to `MemoryFetchCache`; in `Phase.RENDER` store a live result
  whose error is `None`, never one with an error (P-3; Spec: Identical queries are fetched once — "A
  failed fetch is retried")

## 2. Configuration

- [ ] 2.1 `CacheMedium` enum and the `prefetch_cache` key, read and validated in
  `ReportBuilder.__init__` (P-5; Spec: The fetch cache is in memory by default — "Unknown cache medium")

## 3. One fetch step

- [ ] 3.1 Replace `__with_prefetch` and `__render_text` with `__with_fetching(env, record_variables,
  render)`; with `parallelism` 1 it wraps the builders and goes straight to `Phase.RENDER` for
  `make_document()` and for a batch (P-1; Spec: Configurable parallelism with a sequential default;
  Identical queries are fetched once — "A query repeated in a sequential report", "No cache between
  renders"; Batch renders use the parallel pre-fetch — "A fetch shared by the outputs runs once")
- [ ] 3.2 With `parallelism` > 1: one record pass per output, one `prewarm` per batch; a failing record
  pass logs the warning and continues (P-1, P-2; Spec: Batch renders use the parallel pre-fetch — "A
  fetch shared by the outputs runs once", "One output's record pass fails", "Record-pass fallback
  stays in memory")
- [ ] 3.3 Update the 2.1 tests whose expected fetch counts change (`test_parallel_batch_fetches_once_per_output`
  now expects 1 fetch for a query shared by two outputs); every other 2.1 test stays as it is and
  passes (Spec: make_document is unchanged; Parallel batch equals sequential batch)

## 4. Evidence

- [ ] 4.1 `scripts/benchmark_prefetch.py` and `make benchmark` with the four scenarios of design.md
  "Worked example" (P-6)
- [ ] 4.2 Run the benchmark on `master` (2.1.1) and on the branch; both tables go in the PR; the
  acceptance of design.md holds (≥2× on the parallel batch, fetch counts as in the table, memory cache
  not slower than disk)

## 5. Close

- [ ] 5.1 Docs: `docs/modules/ROOT/pages/parallel-execution.adoc` (memoisation, `prefetch_cache`,
  memory note) and the batch section of `api-reference.adoc` (one pre-fetch per batch)
- [ ] 5.2 CHANGELOG 2.2.0 with the two behaviour changes of design.md "Risks"; version 2.2.0 in
  `eds4jinja2/VERSION` and `pyproject.toml`; `make check-all` green
- [ ] 5.3 PR
- [ ] 5.4 Release 2.2.0 on the developer's go-ahead
- [ ] 5.5 Archive the change after the release

## Roadmap

- [ ] 1.1 · [ ] 1.2 · [ ] 2.1 · [ ] 3.1 · [ ] 3.2 · [ ] 3.3 · [ ] 4.1 · [ ] 4.2 · [ ] 5.1 · [ ] 5.2 · [ ] 5.3 · [ ] 5.4 · [ ] 5.5

## Verification

`make check-all`; `make benchmark` on `master` and on the branch; `openspec validate
prefetch-performance --strict`; clarity gate ≥9/10 on this PLAN before task 1.1.
