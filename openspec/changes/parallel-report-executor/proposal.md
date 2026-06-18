<!-- The EPIC — the shaped bet. In Meaningfy the EPIC *is* the OpenSpec proposal. -->

# EPIC: Parallel report executor — pre-warm slow fetches before rendering

## Appetite

**Medium.** One pluggable executor port, a pre-warm/cache orchestration inside
`ReportBuilder.make_document`, a thread-safety fix to `SPARQLClientPool`, config keys, parity and
concurrency tests, a minor version bump. No template-syntax changes, no public-API removals, no
Celery/process executor, no async rewrite. Off by default — the no-config path stays byte-for-byte
identical.

## Why

`eds4jinja2` renders a report by streaming a single Jinja2 template in document order
(`ReportBuilder.make_document` → `template.stream().dump(...)`, `builders/report_builder.py`
~L141). Every `from_endpoint(url).with_query(q).fetch_tabular()` call inside the template runs its
SPARQL query **inline, one after another**, as the renderer reaches it. For the rdf-differ driver
this means a report that issues dozens of slow SPARQL queries serialises them all — **30+ minute
report generation**, dominated entirely by query latency, not by the in-template Python.

The hard truth: **Jinja2 rendering is intrinsically sequential.** `template.stream()` evaluates
expressions in document order and cannot be parallelised — there is no safe way to render two
sections of one template concurrently. So the renderer is the wrong place to look for parallelism.
The only lever is **decoupling data FETCHING from rendering**: run the slow SPARQL fetches in
parallel *before* the render, so that during the render each `fetch_*` reads an already-computed
result instead of waiting on the network. This pays off precisely when the bottleneck is query
latency (the rdf-differ case), and is a no-op when it is in-template Python.

There is also a latent **thread-safety defect** standing in the way: `SPARQLClientPool`
(`adapters/remote_sparql_ds.py`) is a `@singleton` that hands out **one shared `SPARQLWrapper` per
endpoint URL**, and `with_query` MUTATES it via `setQuery`. Two concurrent queries to the same
endpoint clobber each other's query string. Fetching in parallel is impossible until this is fixed,
so the fix is a prerequisite of this change.

## Solution outline

Four moves, all behind an opt-in `parallelism` config key and all backward-compatible:

1. **Discovery (record pass).** Render the template once into a throwaway buffer. During this pass
   each `fetch_*` REGISTERS its `(source-identity, normalised-query)` unit and returns an
   empty/placeholder result instead of executing the query. Collect every registered unit. ALSO
   support an **optional explicit `prefetch` manifest** in `config.json` (a list of source+query
   entries) for determinism and for data-dependent templates where a record pass is unreliable.

2. **Parallel fetch.** Run ALL collected units concurrently via a pluggable executor port (default
   `concurrent.futures.ThreadPoolExecutor(max_workers=N)`), where `N` is `parallelism` from config
   (e.g. 2/4/16/32/64). Wait for ALL to complete. **ALL-OR-NOTHING**: if any unit raises, ABORT the
   whole report — no output file is produced, the error is surfaced. No mid-way recovery, no retry,
   no partial results.

3. **Render.** The real render. Each `fetch_*` now serves its result from the cache (cache HIT).
   Any query NOT in the cache (e.g. a data-dependent query the record pass could not predict) runs
   LIVE/sequentially as a graceful fallback — slower, but correct.

4. **Cleanup.** Results are staged in a TEMP FOLDER keyed by a hash of
   `(source-identity + normalised-query)`. The temp folder is REMOVED after rendering finishes — on
   success AND on failure (try/finally). Because the cache is keyed by query hash, **identical
   queries are fetched only once** within a run (memoisation is free).

The **consumer pattern** (config, not code): keep templates untouched — they still call
`from_endpoint(...).with_query(...).fetch_tabular()` — and just set `"parallelism": 16` in
`config.json`. `eds4jinja2` itself drives the parallelism; the consumer only turns it on.

## Key decisions

- **DEC-1 (pre-warm over section-parallel/async)**: decouple fetching from rendering — record pass,
  parallel fetch, then render-from-cache — chosen over parallelising the render and over an
  async/await rewrite. Jinja2's `template.stream()` is sequential by construction; the fetch is the
  only thing that can be moved off the critical path. Pre-warm also maps directly onto the
  temp-folder cache mechanism the driver asked for. *(Alternatives: section-parallel rendering —
  rejected, Jinja2 cannot render concurrently and it would mean a template-syntax change; async/await
  — rejected, would require rewriting the whole render path and every data source for almost no gain
  over threads on I/O-bound work.)*
- **DEC-2 (threads only, pluggable port)**: a small `Executor` port (`map(fn, items, max_workers)`),
  default implementation wrapping `concurrent.futures.ThreadPoolExecutor`. Network I/O to remote
  endpoints and oxigraph in-memory queries RELEASE the GIL → real speedup; rdflib in-memory queries
  are pure-Python/GIL-bound → limited speedup but still correct. A documented SEAM is left for a
  future Celery/process executor but it is NOT built (YAGNI — Celery needs a broker and cannot share
  an in-memory graph cheaply). *(Alternatives: processes/Celery now — rejected, cannot cheaply share
  an in-memory graph and add a broker dependency for no I/O-bound benefit.)*
- **DEC-3 (all-or-nothing)**: if any pre-warm fetch raises, abort the whole report; no output file,
  no partial results, no retry, no checkpoint/resume. Explicit decision from the driver: a partial
  report is worse than a failed one.
- **DEC-4 (off by default — backward compat)**: parallelism is OPT-IN. Default `parallelism = 1`
  (or unset) → today's exact sequential behaviour, byte-for-byte: no record pass, no temp folder, no
  executor. A no-config `ReportBuilder` behaves identically to before.
- **DEC-5 (eds4jinja2 drives orchestration)**: the pre-warm / fetch / render / cleanup loop lives
  inside `ReportBuilder.make_document` (the existing single orchestration point), not in the
  consumer and not in the data sources. The data sources only gain cache-aware fetching.
- **DEC-6 (SPARQLClientPool thread-safety fix — in scope)**: stop sharing one mutable `SPARQLWrapper`
  across threads. Create a per-call (or per-thread) `SPARQLWrapper` so the mutable query string is
  never shared; keep connection reuse only where it is safe. A regression test proves concurrent
  queries to one endpoint do not clobber each other.
- **DEC-7 (record-pass discovery WITH optional explicit manifest)**: discover units by a record pass
  by default, but allow an explicit `prefetch` manifest in `config.json` for determinism and for
  data-dependent templates. Queries missed by discovery run live during the render (graceful
  fallback), never crash.

## Rabbit-holes

- Do **not** try to parallelise Jinja2 rendering itself. The render stays a single sequential
  `template.stream().dump(...)`. Only fetching is moved.
- Do **not** build a process/Celery executor in this change. Define the port and a default thread
  implementation; leave the rest as a documented seam.
- Do **not** add retry, checkpoint, resume, or partial-result logic. All-or-nothing is the contract.
- Do **not** over-model the manifest. It is a list of `{source, query}` entries; nothing more.
- Avoid persisting the temp cache across runs in this change (it is an Open Question — parked).
- Do **not** re-key the cache on anything other than `(source-identity + normalised-query)` — that
  is what makes memoisation free and keeps the record-pass and manifest paths consistent.

## No-gos

<!-- MANDATORY. Explicitly out of scope. -->

- **No change to the sequential default.** With `parallelism` unset or `1`, behaviour is byte-for-byte
  identical to today — no record pass, no temp folder, no executor.
- **No Celery / multiprocessing** in this change — a documented executor seam only.
- **No partial-failure recovery / retry / resume / checkpointing.** All-or-nothing.
- **No async/await rewrite** of the Jinja2 render path or the data sources.
- **No section-parallel rendering** in this change (parked future alternative — see Open Questions).
- **No template-syntax changes.** Templates stay byte-for-byte unchanged; parallelism is config-only.
- **No break** to the public contracts of the existing two data sources
  (`RemoteSPARQLEndpointDataSource`, `RDFFileDataSource`) or the `DataSource` ABC's `(result, error)`
  fail-safe wrappers.
- **No new mandatory heavy dependency.** The default executor is stdlib `concurrent.futures`.

---

## What Changes

- Add an `Executor` port and a default `ThreadPoolExecutor`-backed implementation
  (`builders/`), with a documented seam for a future process/Celery executor.
- Add a pre-warm orchestration to `ReportBuilder.make_document` (`builders/report_builder.py`):
  record pass → parallel fetch → render-from-cache → temp-folder cleanup (try/finally). Gated by
  `parallelism`; with `parallelism <= 1` the existing single `template.stream().dump(...)` path runs
  unchanged.
- Make the data-source builders cache-aware so that during the record pass `fetch_*` registers its
  unit (and returns a placeholder) and during the real render `fetch_*` serves from the temp-folder
  cache, falling back to a live fetch on a cache miss.
- Fix `SPARQLClientPool` (`adapters/remote_sparql_ds.py`) so concurrent queries to the same endpoint
  use isolated `SPARQLWrapper` query state — never a shared mutable query string.
- Define config-key constants (no free strings): `parallelism` (int, default 1), optional `prefetch`
  manifest, optional temp-dir override (default a `tempfile.mkdtemp`).
- Add unit tests (executor port, cache keying/memoisation, record pass, all-or-nothing abort, cleanup
  on success and failure), a concurrency regression test for `SPARQLClientPool`, and a parity test
  proving parallel and sequential runs produce identical output.
- Bump version 0.3.1 → 0.4.0 and add a changelog/README note. **MINOR, non-breaking.**

## Capabilities

### New Capabilities
- `parallel-report-executor`: optionally fetch a report's SPARQL data in parallel before rendering
  (pre-warm + temp-folder cache, threads only, all-or-nothing), driven by `eds4jinja2` and turned on
  via a `parallelism` config key, with templates unchanged and sequential default behaviour preserved.

### Modified Capabilities
<!-- None: no existing spec carries requirements for these areas yet. -->

## Impact

- **Code**: `eds4jinja2/builders/report_builder.py` (pre-warm orchestration in `make_document`),
  `eds4jinja2/builders/jinja_builder.py` (cache-aware data-source builders), new executor module under
  `eds4jinja2/builders/`, `eds4jinja2/adapters/remote_sparql_ds.py` (thread-safety fix), new tests
  under `tests/unit/`.
- **APIs**: `config.json` gains optional `parallelism`, `prefetch`, and temp-dir keys (additive). No
  public signature removed. The executor port is new public surface.
- **Dependencies**: none added (default executor is stdlib `concurrent.futures`).
- **Version**: 0.3.1 → 0.4.0 (MINOR).
- **Golden thread / driver**: the consumer is **rdf-differ's long-running report generation** (30+ min
  reports). This change **builds on `in-memory-sparql-datasource`** (data sources must be safe for
  concurrent reads) and is **complementary to `builtin-graph-store`** (oxigraph in-memory queries are
  exactly where threading pays off for in-memory graphs).
