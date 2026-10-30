<!-- SECONDARY input — preserved, never groomed. The EPIC (proposal.md) supersedes it. -->

# Seeds and Q&A — parallel-executor-hardening

## Human seed (2026-10-30)

> "Is there any way to adopt, implement, or use if it exists already, any parallelisation feature
> for Jinja? We often run long queries, and that could be a pain if the runs are sequential … the
> query calls are inside the templates so those could somehow be executed before the page is
> rendered, or identify such calls in the template and run them in parallel? … we shall explore and
> write a new epic change about this."

Follow-up: "draft a new epic pitch that strengthens the current approach".

## Inputs read

- `openspec/specs/parallel-report-executor/spec.md` (the durable truth).
- `openspec/changes/archive/2026-06-19-parallel-report-executor/proposal.md` (the original bet).
- `eds4jinja2/services/parallel_executor.py`, `eds4jinja2/services/report_builder.py`
  (`make_document`, `__make_document_parallel`).
- `eds4jinja2/adapters/remote_sparql_ds.py` (`SPARQLClientPool`, already per-thread).
- `docs/modules/ROOT/pages/parallel-execution.adoc`.

## Findings (exploration, 2026-10-30)

1. **The feature already exists.** Record pass → parallel pre-warm → render-from-cache, opt-in via
   `parallelism` in `config.json`. Archived 2026-06-19.
2. **Data-dependent fetches are not parallelised.** During the record pass every `fetch_*` returns
   an empty placeholder, so loops over a fetched result (`{% for x in a.fetch_tabular()[0] %}` →
   one query per row) do not iterate and their inner queries are never recorded. They run live,
   sequentially, during the real render — the slowest pattern is the one left unaccelerated.
3. **Placeholder fragility → silent full fallback.** Templates that index into results
   (`df.iloc[0]`, `rows[0]`) raise during the record pass; `__make_document_parallel` then logs a
   single WARNING and renders the whole report sequentially. The user believes it is parallel.
4. **Spec ↔ code drift.** The spec promises an optional `prefetch` manifest (and DEC-7 of the
   archived EPIC); no code implements it.
5. **No per-endpoint throttle.** `parallelism: 32` means up to 32 concurrent requests to a single
   endpoint (risk: overloading Fuseki / public endpoints, 429/503 → all-or-nothing abort).
6. **No observability.** Nothing reports how many units were pre-warmed, cache hits vs live misses,
   or which queries were slowest.

## Alternatives considered and rejected in conversation

- Jinja2 `enable_async`: awaits calls in document order — no concurrency without rebuilding the
  data sources around futures.
- Static analysis of the template AST: breaks when queries are built from variables (the common
  case).
- Lazy futures returned from `fetch_*`: only helps when templates fetch early; ours consume
  results immediately.

## Q&A record

- Draft 1 listed five open questions (wave cap, strict mode, per-endpoint limit shape, manifest
  drop, benchmark criterion) with proposed defaults.
- 2026-10-30, developer: "go ahead, and also commit in this branch" → proposed defaults adopted;
  see `proposal.md` → *Decision record* (DEC-4, DEC-8 … DEC-11).
