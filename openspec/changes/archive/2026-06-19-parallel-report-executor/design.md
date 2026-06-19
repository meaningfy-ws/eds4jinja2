<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Parent: EPIC `parallel-report-executor` (proposal.md) — derived from DEC-1..DEC-7.

## Context

`eds4jinja2` renders a report from one Jinja2 template. `ReportBuilder.make_document`
(`builders/report_builder.py`, ~L134-144) is the single orchestration point:

```python
def make_document(self):
    for listener in self.__before_rendering_listeners:
        listener(self.configuration_context)
    template = self.__get_template(self.template)
    pathlib.Path(self.configuration_context["output_folder"]).mkdir(parents=True, exist_ok=True)
    template.stream().dump(str(pathlib.Path(self.configuration_context["output_folder"]) / self.template))
    for listener in self.__after_rendering_listeners:
        listener(self.configuration_context)
```

`template.stream().dump(...)` evaluates the template in document order. Each
`from_endpoint(url).with_query(q).fetch_tabular()` (builders from `DATA_SOURCE_BUILDERS`,
`builders/jinja_builder.py`) issues its SPARQL query **inline and serially** as the renderer reaches
it. Jinja2 streaming is sequential by construction — there is no concurrency hook in the render path.

The remote source (`adapters/remote_sparql_ds.py`) is the latency bottleneck and is **not
thread-safe**:

```python
@singleton
class SPARQLClientPool(object):
    connection_pool = {}
    @staticmethod
    def create_or_reuse_connection(endpoint_url: str):
        if endpoint_url not in SPARQLClientPool.connection_pool:
            SPARQLClientPool.connection_pool[endpoint_url] = SPARQLWrapper(endpoint_url)
        return SPARQLClientPool.connection_pool[endpoint_url]
```

`RemoteSPARQLEndpointDataSource.with_query` then calls `self.endpoint.setQuery(new_query)` on that
**shared** wrapper, and `_fetch_*` reads `self.endpoint.queryString`. Two threads querying the same
endpoint clobber each other's query string. Concurrent fetching is impossible until this is fixed.

The `DataSource` ABC (`adapters/base_data_source.py`) defines the fail-safe wrappers
(`fetch_tabular` / `fetch_tree` returning `(result, error)`) over the abstract
`_can_be_*` / `_fetch_*`. The fluent `with_query(...)` → `self` style is shared across sources.

**Constraints**: layers `entrypoints > builders > adapters` (adapters innermost — import-linter
enforced; the executor port lives in `builders`, which may use `adapters`); Python 3.11/3.12; pip +
tox + pyproject; default executor must be stdlib (`concurrent.futures`); no new mandatory dependency.

## Goals / Non-Goals

**Goals:**
- Cut wall-clock time for latency-bound reports by fetching SPARQL data in parallel **before** the
  render, then rendering from a cache — with **unchanged templates**.
- Drive the parallelism inside `eds4jinja2`; the consumer only sets `parallelism` in `config.json`.
- Keep the sequential default **byte-for-byte identical** (no record pass, no temp folder, no executor
  when `parallelism <= 1`).
- Fix `SPARQLClientPool` so concurrent same-endpoint queries are isolated.
- Make memoisation free: identical `(source, query)` fetched once per run.

**Non-Goals:**
- No parallel/async Jinja2 rendering; no section-parallel rendering.
- No Celery/process executor (seam only); no retry/resume/checkpoint; no partial results.
- No template-syntax change; no change to the existing data sources' public contracts.
- No cross-run cache persistence (parked).

## Decisions

- **DEC-1 (pre-warm over section-parallel/async)**: orchestrate `record pass → parallel fetch →
  render-from-cache → cleanup` inside `make_document`. The render stays one sequential
  `template.stream().dump(...)`. *(Why: Jinja2 streaming cannot be parallelised; fetching is the only
  movable cost, and pre-warm maps directly onto the temp-folder cache. Alternatives in proposal.md.)*
- **DEC-2 (Executor port, threads only)**: define an `Executor` protocol with
  `map(fn, items, *, max_workers) -> list` (raise on first failure, ALL_COMPLETED otherwise). The
  default `ThreadPoolExecutor`-backed implementation wraps `concurrent.futures`. The port is the only
  concurrency seam; a future `ProcessExecutor`/`CeleryExecutor` can be slotted in without touching
  `ReportBuilder`. *(Why: I/O-bound + GIL-releasing in-memory engines benefit from threads; processes
  cannot cheaply share an in-memory graph.)*
- **DEC-3 (cache key = hash of source-identity + normalised query)**: a `PrefetchUnit` is identified
  by `sha256(source_identity + "\n" + normalised_query)`. `source_identity` is the source's stable
  string identity (e.g. endpoint URL for remote, a store id for in-memory); `normalised_query` is the
  fully-substituted prefixed query string the source would execute. The same key drives the record
  pass, the parallel fetch, the render-time cache lookup, and free memoisation. *(Why: one key, one
  store, consistent across discovery and render.)*
- **DEC-4 (two-phase, mode-switched data-source fetch)**: the data-source builders become cache-aware
  via an injected `PrefetchContext` (mode = `RECORD | SERVE | LIVE`). In `RECORD` mode `fetch_*`
  registers its unit and returns an empty placeholder (empty `DataFrame` / empty SPARQL-JSON) without
  executing. In `SERVE` mode `fetch_*` reads the staged result for its key from the temp folder; on a
  cache MISS it falls back to a real LIVE fetch (graceful). With no context (`parallelism <= 1`) the
  builders behave exactly as today. *(Why: keeps templates and the fail-safe `(result, error)`
  contract intact; the only change is where the bytes come from.)*
- **DEC-5 (all-or-nothing)**: `Executor.map` waits for ALL units; the first exception aborts the whole
  pre-warm and propagates out of `make_document` **before** any output file is written. No retry, no
  partial render. *(Why: explicit driver requirement.)*
- **DEC-6 (temp-folder staging + try/finally cleanup)**: results are written into a temp folder
  (default `tempfile.mkdtemp(prefix="eds4jinja2-prefetch-")`, overridable via config). The folder is
  removed in a `finally` block that wraps the fetch+render so it is cleaned on success AND on failure.
  *(Why: bounded memory for large result sets; deterministic cleanup; the driver asked for a temp
  folder.)*
- **DEC-7 (SPARQLClientPool thread-safety fix)**: stop mutating one shared `SPARQLWrapper`. Keep the
  pool keyed by endpoint URL for connection reuse, but give each fetch its own query state — create a
  fresh `SPARQLWrapper(endpoint_url)` per call (or per thread via `threading.local`) so the mutable
  `queryString` is never shared across threads. `RemoteSPARQLEndpointDataSource.__str__` and the
  `(result, error)` contract are preserved. *(Why: prerequisite for any concurrent fetch.)*
- **DEC-8 (record pass + optional manifest)**: discover units by a `RECORD`-mode render into a
  throwaway buffer. If `config.json` carries a `prefetch` manifest (list of `{source, query}`
  entries), those units are added/seeded too, giving determinism for data-dependent templates.
  Queries that neither the record pass nor the manifest predicted (e.g. a query whose text depends on
  data fetched mid-render) are simply not in the cache and run LIVE during the render. *(Why:
  determinism where wanted, graceful degradation everywhere else.)*
- **DEC-9 (config-key constants, no free strings)**: `CONFIG_PARALLELISM = "parallelism"`,
  `CONFIG_PREFETCH = "prefetch"`, `CONFIG_PREFETCH_TEMP_DIR = "prefetch_temp_dir"`, plus
  `PREFETCH_SOURCE = "source"` / `PREFETCH_QUERY = "query"` for manifest entries, and a `PrefetchMode`
  enum (`RECORD`/`SERVE`/`LIVE`). No semantic label exists only as a raw string.

## Algorithm / approach

**A. Executor port** (`builders/executor.py`):
```python
class Executor(Protocol):
    def map(self, fn, items, *, max_workers: int) -> list: ...

class ThreadPoolExecutorAdapter:
    def map(self, fn, items, *, max_workers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(fn, item) for item in items]
            done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
            return [f.result() for f in futures]   # first .result() raising aborts all-or-nothing
# Seam: a future ProcessExecutorAdapter / CeleryExecutorAdapter implements the same .map — NOT built here.
```

**B. ReportBuilder.make_document orchestration** (`builders/report_builder.py`):
```python
def make_document(self):
    for listener in self.__before_rendering_listeners:
        listener(self.configuration_context)
    parallelism = int(self.configuration_context.get(CONFIG_PARALLELISM, 1))
    template = self.__get_template(self.template)
    out = str(pathlib.Path(self.configuration_context["output_folder"]) / self.template)
    pathlib.Path(self.configuration_context["output_folder"]).mkdir(parents=True, exist_ok=True)

    if parallelism <= 1:
        template.stream().dump(out)                      # DEC-4: unchanged sequential path
    else:
        ctx = PrefetchContext(temp_dir=self._prefetch_temp_dir())   # DEC-6
        try:
            # 1. RECORD: throwaway render registers units; seed from manifest (DEC-8)
            ctx.mode = PrefetchMode.RECORD
            self._inject_prefetch_context(ctx)
            template.render()                            # throwaway buffer; placeholders returned
            ctx.seed_from_manifest(self.configuration_context.get(CONFIG_PREFETCH, []))
            # 2. FETCH: all units concurrently, all-or-nothing (DEC-5)
            self._executor.map(ctx.fetch_unit, ctx.units(), max_workers=parallelism)
            # 3. SERVE: real render reads cache; misses fall back to LIVE (DEC-4)
            ctx.mode = PrefetchMode.SERVE
            template.stream().dump(out)
        finally:
            ctx.cleanup()                                # DEC-6: success AND failure
    for listener in self.__after_rendering_listeners:
        listener(self.configuration_context)
```
(`self._executor` defaults to `ThreadPoolExecutorAdapter()`, injectable for tests. On a fetch
exception the `_executor.map` raises inside the `try`, `finally` cleans the temp folder, and the
exception propagates — **no output file is written**. The `parallelism <= 1` branch never builds a
context or temp folder, so it is byte-for-byte today's behaviour.)

**C. Cache-aware data sources** (`builders/jinja_builder.py` + the data sources):
- A `PrefetchUnit` carries `source_identity`, `normalised_query`, and a `key`
  (`sha256(source_identity + "\n" + normalised_query)`), and knows how to `execute()` against its real
  source and how to read/write its staged result file under `ctx.temp_dir / key`.
- The `from_endpoint` (and `from_memory`, when present) builders consult the active `PrefetchContext`:
  - `RECORD`: `fetch_*` computes the unit's `key`, registers the unit, returns an empty placeholder.
  - `SERVE`: `fetch_*` returns the staged result for its `key`; on miss it executes LIVE and returns
    the real result (and the wrapper's `(result, error)` contract is unchanged).
  - no context: today's direct fetch.
- **Memoisation (DEC-3)**: `ctx.register(unit)` dedupes by `key`, so identical `(source, query)` pairs
  collapse to a single unit fetched once.

**D. SPARQLClientPool thread-safety fix** (`adapters/remote_sparql_ds.py`):
```python
@singleton
class SPARQLClientPool(object):
    connection_pool = {}        # endpoint_url -> threading.local (or a per-call factory)
    @staticmethod
    def create_or_reuse_connection(endpoint_url: str):
        # return a SPARQLWrapper whose mutable queryString is NOT shared across threads:
        # a fresh wrapper per call, or one per (endpoint_url, thread) via threading.local.
        ...
```
The query string is never shared; connection reuse is kept only where it is provably safe.
`with_query`/`_fetch_*`/`__str__` keep their signatures and the `(result, error)` contract.

**Worked example (consumer, templates unchanged):**
```jsonc
// config.json  — the ONLY change a consumer makes
{ "template": "main.html", "conf": { ... }, "parallelism": 16 }
```
```python
ReportBuilder(target_path="report/").make_document()
# template still calls {{ from_endpoint(conf.default_endpoint).with_query(q).fetch_tabular() }}
# now: 16 queries fetched concurrently before render, render reads from cache, temp folder removed.
```
Optional deterministic manifest for a data-dependent template:
```jsonc
{ "parallelism": 16,
  "prefetch": [ {"source": "from_endpoint:http://ep/sparql", "query": "SELECT ..."} ] }
```

### Anti-patterns
- ❌ Trying to render two template sections concurrently (Jinja2 streaming is sequential — only
  fetching is parallel).
- ❌ Sharing one mutable `SPARQLWrapper` across threads (the defect this change fixes).
- ❌ Building a `ProcessExecutor`/`CeleryExecutor` now (seam only — YAGNI; a broker + un-shareable
  in-memory graph for no I/O-bound gain).
- ❌ Returning partial output when a pre-warm fetch fails (all-or-nothing — abort, no file).
- ❌ Leaving the temp folder behind on failure (cleanup must be in `finally`).
- ❌ Creating a record pass / temp folder when `parallelism <= 1` (must be byte-for-byte the old path).
- ❌ Free strings for config keys, manifest fields, or modes — use `CONFIG_*` / `PREFETCH_*` constants
  and the `PrefetchMode` enum.
- ❌ Re-fetching identical `(source, query)` pairs (dedupe by cache key — memoisation is free).

## Error matrix

| Failure mode | Expected handling |
|---|---|
| One pre-warm fetch raises (bad SPARQL, endpoint down) | `Executor.map` raises on first failure → whole report ABORTED inside the `try`; `finally` removes the temp folder; **no output file is written**; the error is surfaced (DEC-5) |
| Record pass mis-predicts a data-dependent query | the query's key is absent from the cache → it runs LIVE during the `SERVE` render (graceful, slower, no crash) (DEC-8) |
| Temp-folder cleanup on success | `finally` removes the temp folder after a successful render (DEC-6) |
| Temp-folder cleanup on failure | same `finally` removes the temp folder when the fetch/render aborts (DEC-6) |
| `parallelism` unset or `1` | sequential `template.stream().dump(...)`; no record pass, no executor, **no temp folder created**; byte-for-byte today (DEC-4) |
| Two threads querying the same endpoint with different queries | each gets its own correct result — no shared mutable `SPARQLWrapper` query string (DEC-7) |
| Identical `(source, query)` appears twice in a report | registered once (deduped by cache key) and fetched a single time (DEC-3) |
| `prefetch` manifest entry malformed (missing `source`/`query`) | rejected at seed time with a clear error before any fetch starts (fail fast) |
| Empty result from a pre-warm query | staged as an empty `DataFrame` / empty SPARQL-JSON; served on render without error |

## Risks / Trade-offs

- **[Parallel vs sequential output drift]** → Mitigation: a parity test renders the same report with
  `parallelism=1` and `parallelism=N>1` and asserts byte-identical output; the cache-aware `SERVE`
  path must return exactly what a live fetch would.
- **[Record-pass side effects / non-determinism]** → Mitigation: the record render targets a throwaway
  buffer and `fetch_*` returns inert placeholders; the optional manifest gives a deterministic path
  for data-dependent templates; missed queries fall back to LIVE.
- **[Thread-safety regressions beyond SPARQLClientPool]** → Mitigation: a concurrency regression test
  fires N threads at one endpoint with distinct queries and asserts each receives its own result; the
  fix isolates the only shared mutable state.
- **[rdflib in-memory queries are GIL-bound]** → Mitigation: documented — threads still produce correct
  results, just less speedup; remote endpoints and oxigraph (GIL-releasing) are where the win lands.
  See the table below.
- **[Temp-folder leak]** → Mitigation: cleanup in `finally`; a test asserts the folder is gone after
  both a successful and an aborted run.
- **[Backward-compat regression]** → Mitigation: an explicit test runs a no-`parallelism` config and
  asserts no executor/record-pass/temp-folder is created and output is unchanged.

**Where threading pays off (GIL behaviour):**

| Data source | Work type | GIL during fetch | Speedup from threads |
|---|---|---|---|
| Remote SPARQL endpoint | network I/O | released | high |
| In-memory oxigraph store | C-extension query | released | high |
| In-memory rdflib graph | pure-Python query | held | limited (still correct) |
| Tabular file (pandas) | mostly C / I/O | mostly released | moderate |

## Open Questions

- Persisting the temp cache across runs for fast dev re-runs (skip re-fetch when query+graph
  unchanged). *(Parked: a separate caching concern; default is per-run mkdtemp + cleanup.)*
- Section-parallel rendering as a future alternative if a consumer's bottleneck ever moves into
  in-template Python rather than fetch latency. *(Parked: would need a template-syntax/render-model
  change; out of scope here — see No-gos.)*
- Whether `source_identity` for in-memory stores needs a richer identity than a store id when two
  distinct graphs share a builder key. *(Parked: low risk for the rdf-differ driver, which uses one
  store per report.)*
