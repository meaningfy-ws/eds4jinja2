# Seed: performance review after 2.1.1, 2026-10-31 (secondary; never groomed)

Asked by the developer: "are you aware of any other ways to improve the performance?" The answer,
from reading the code (nothing measured), ranked seven candidates:

1. **One pre-fetch per batch.** `render_documents` builds a `FetchCoordinator` per output: one record
   pass, one parallel pre-warm and one cleanup per output, in sequence. A query shared by several
   outputs runs once per output. Cache keys are `sha256(repr((source_id, query_repr, method)))`, so one
   coordinator can serve a whole batch.
2. **In-memory fetch cache.** `FetchCache` pickles every result to a temp folder and unpickles it on
   read. For in-memory graphs that round-trip can cost more than the query.
3. **oxigraph for in-memory graphs.** rdflib queries hold the GIL; `engine="oxigraph"` exists already.
4. **Memoise identical fetches in sequential mode.** With `parallelism` 1 a query a template repeats
   runs every time.
5. **Keep parallelism when the record pass fails** (the closed `parallel-executor-hardening` waves).
6. **HTTP keep-alive** for remote SPARQL (SPARQLWrapper uses `urllib`, a connection per query).
7. **Overlay recompiles**: each `autoescape` batch compiles its template again.

## Decisions taken with the developer (Q&A, 2026-10-31)

- **Scope:** items 1, 2 and 4. ("Also memoise sequential runs" chosen over the recommended 1+2.)
- **Cache:** memory by default, the temp folder kept as an opt-in for very large reports. The temp
  folder was the mechanism the original driver (rdf-differ) asked for, to bound memory.
- **Evidence:** a benchmark script in the repo with a fake data source that sleeps per query (no
  network), comparing before and after on a 20-output batch; the result is recorded in the PR.
