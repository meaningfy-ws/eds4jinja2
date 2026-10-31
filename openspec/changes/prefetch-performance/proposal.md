<!-- The EPIC — the shaped bet. In Meaningfy the EPIC *is* the OpenSpec proposal. -->

# EPIC: Prefetch performance — one pre-fetch per batch, results in memory, no repeated query

## Appetite

**MEDIUM.** Three improvements to the existing fetch path of `ReportBuilder`
(`services/parallel_executor.py`, `services/report_builder.py`), with a benchmark. No new public
method; one new configuration key. Released as minor version 2.2.0.

Seeds: [`inputs/seed.md`](inputs/seed.md) (the performance review and the decisions taken with the
developer). Golden-thread parents: capabilities `parallel-report-executor` and
`batch-document-rendering`.

## Why

A report's time goes into its data fetches, and three parts of today's fetch path repeat work:

- A batch of N outputs (`render_documents`, `make_documents`) runs N separate record passes and N
  parallel pre-warms one after another, and a query that several outputs share runs once per output.
- Every pre-warmed result is pickled to a temp folder and unpickled on each read. For an in-memory
  graph this round-trip can cost more than the query itself.
- Without `parallelism`, a query that a template repeats (in a loop, in two sections) runs every
  time.

rdf-fingerprinter renders one batch output per named graph through 2.1's batch methods, so it pays
all three costs on every run.

## Solution outline

The outcome: **every distinct fetch of a render — a single report or a whole batch — runs once, the
parallel ones in a single pre-warm, and its result is served from memory.**

1. **One pre-fetch per batch.** A batch records every output's fetches first, pre-warms their union
   once in parallel, then renders every output from that cache. `make_document()` is the batch of one.
2. **Results in memory.** The pre-warm cache keeps results in memory by default. The temp-folder
   cache stays available through configuration for reports whose results do not fit in memory.
3. **No repeated query, sequential too.** With `parallelism` unset or 1, identical fetches within one
   render (or one batch) run once; later uses get the stored result.
4. **Proof.** A benchmark in the repo, with a data source that sleeps per query, shows the gain on a
   20-output batch; deterministic tests pin the fetch counts.

## Key decisions

- **DEC-1**: Scope is the batch pre-fetch, the memory cache and sequential memoisation — reason: they
  remove repeated work without changing any template or API. Seed item 5 (keep parallelism after a
  failed record pass) is adopted only as far as a batch needs it: the fetches recorded before the
  failure stay in the batch's pre-warm (design P-2); the discovery "waves" of the closed
  `parallel-executor-hardening` change are not. Rejected for now: HTTP keep-alive and overlay reuse
  (seed items 6–7), and switching the default engine to oxigraph (seed item 3).
- **DEC-2**: Memory cache by default, temp folder opt-in through a configuration key — reason: most
  reports' results fit in memory and the pickle round-trip is pure overhead; the temp folder was asked
  for by the original driver (rdf-differ) to bound memory and stays available; rejected: memory only
  (big reports lose their bound), keeping the temp folder as default (keeps the overhead for everyone).
- **DEC-3**: Memoisation also applies with `parallelism` unset or 1 — reason: repeated queries are
  common in templates and cost a full round-trip each; the developer chose it over leaving the default
  path untouched. This is a **behaviour change** for the default path: a query that returns different
  results on each call (`RAND()`, `NOW()`) returns the first result for the rest of that render. The
  "same output" promises of the specs therefore hold for deterministic queries, and say so.
- **DEC-4**: A stored result is handed out as a copy — reason: templates and helpers may change a
  DataFrame in place (the template helper `simplify_uri_columns_in_tabular` defaults to `inplace=True`); today's pickle cache
  hands out a fresh object on each read and this must hold; rejected: sharing one object (a mutation
  in one section would leak into another).
- **DEC-5**: Fetch errors are not stored — reason: today a failed query is retried when the template
  calls it again, and pre-warm already aborts on any error; storing errors would turn one transient
  failure into many; rejected: storing them.
- **DEC-6**: Evidence is a repo benchmark with a fake per-query latency, not a CI gate — reason:
  timings on shared runners are noisy; the benchmark is run by hand and its numbers go in the PR,
  while fetch-count tests in the gate prove the mechanism; rejected: a timing assertion in CI, a real
  rdf-fingerprinter run (needs its data and environment).

## Rabbit-holes

- Cache keys must identify a fetch exactly across outputs. Two different data sources that produce
  the same key would wrongly share a result. Keys come from the builder name and its arguments; an
  argument without a value-based `repr` gets an identity-based one, which can only cause a cache miss,
  never a wrong hit.
- A failed record pass for one output must not abort or degrade the other outputs of the batch.
- Memory: a batch now holds the union of all its outputs' results at once. The disk opt-in (DEC-2) is
  the escape hatch.
- Copying large DataFrames on every read has a cost; it must stay well below a query's.

## No-gos

- No change to templates, to the data-source API, or to the signatures of `make_document`,
  `render_documents` or `make_documents`.
- No HTTP-layer change, no new dependency, no change of the default graph engine (DEC-1).
- No timing assertion in CI (DEC-6).
- No cache that outlives one render or one batch: nothing is shared between calls.

---

## What Changes

- A batch pre-fetches once: one coordinator, one record pass per output, one parallel pre-warm.
- The pre-warm cache is in memory by default; a new configuration key selects the temp-folder cache.
- Identical fetches are memoised within one render or batch, with or without `parallelism`.
- A benchmark script and a `make` target to run it; CHANGELOG; docs (`parallel-execution.adoc`).
- Version 2.2.0 (DEC-3 changes default behaviour for queries with non-deterministic results).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `parallel-report-executor`: the sequential default memoises identical fetches; the cache is in
  memory by default with a temp-folder opt-in.
- `batch-document-rendering`: a batch is pre-fetched once, not once per output.

## Impact

- Code: `eds4jinja2/services/parallel_executor.py`, `eds4jinja2/services/report_builder.py`.
- Tests: `tests/unit/services/`; a benchmark script outside the test suite.
- Docs: `docs/modules/ROOT/pages/parallel-execution.adoc`, the `ReportBuilder` API page, CHANGELOG.
- Consumers: rdf-fingerprinter gets faster without code changes; reports that relied on repeated
  queries returning different results (DEC-3) must be told in the release notes.
