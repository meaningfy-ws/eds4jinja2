<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [x]` checkboxes. -->

> Derived from EPIC `builtin-graph-store` (proposal.md)  <!-- cite your parent (golden thread) -->

> Depends on the sibling change `in-memory-sparql-datasource` (provides `InMemorySPARQLDataSource`).

## 1. Graph store port + rdflib engine (TDD: tests first)

- [x] 1.1 Write failing unit tests `tests/unit/test_graph_store.py`: `Engine("rdflib")` and `Engine("oxigraph")` resolve; `Engine("jena")` raises `ValueError`
- [x] 1.2 Add failing test: `RdflibGraphStore` loads a single Turtle file and `query` returns rdflib `Result` bindings for a SELECT
- [x] 1.3 Add failing test: `make_graph_store(Engine.RDFLIB, sources=["a.ttl", "b.ttl"])` loads multiple sources into one graph (union queryable)
- [x] 1.4 Add failing test: `make_graph_store` loads each source EXACTLY ONCE — patch the store's `load`, run two queries against the returned store, assert one `load` call per source (no per-query re-parse)
- [x] 1.5 Add failing test: rdflib path constructs and queries with `pyoxigraph` ABSENT (monkeypatch the import) — no `ImportError` on the default path
- [x] 1.6 Implement `eds4jinja2/adapters/graph_store.py` — `Engine(str, Enum)`, `GraphStorePort(ABC)`, `RdflibGraphStore`, the `_STORE_BY_ENGINE` dispatch map, `make_graph_store(engine, sources=None, graph=None)` (load each source once), `_is_url`/`_normalise_sources` helpers; make tests pass

## 2. oxigraph engine (opt-in, lazy import) (TDD)

- [x] 2.1 Write failing test: `OxigraphGraphStore` requested with `pyoxigraph` not installed raises `ImportError` whose message names `eds4jinja2[oxigraph]`
- [x] 2.2 Write failing test (skipped unless `pyoxigraph` installed): `OxigraphGraphStore` loads a file and `query` returns solutions consumable by `InMemorySPARQLDataSource`
- [x] 2.3 Write failing test: `OxigraphGraphStore.load` of a URL fetches bytes via `requests` (mock `requests.get`) then loads them; assert `pyoxigraph` is NOT imported at module top
- [x] 2.4 Implement `OxigraphGraphStore` in `graph_store.py` — lazy `_import_pyoxigraph` with actionable error, `load` (file vs URL via `requests`), `query`; wire into `_STORE_BY_ENGINE`; make tests pass

## 3. from_rdf builder registration (TDD)

- [x] 3.1 Write failing `tests/unit/test_jinja_builder.py` assertion that `from_rdf` is in `DATA_SOURCE_BUILDERS` and builds an `InMemorySPARQLDataSource` (default engine rdflib)
- [x] 3.2 Write failing test: `from_rdf("dataset.ttl")` then `with_query(...)._fetch_tabular()` returns a `pd.DataFrame`, and `_fetch_tree()` returns the SPARQL-JSON dict shape (parity inherited from `InMemorySPARQLDataSource`)
- [x] 3.3 Write failing test: `from_rdf(sources, engine="oxigraph")` routes to the oxigraph store (skipped unless `pyoxigraph` installed); `sources` accepts both a single string and a list
- [x] 3.4 Register `from_rdf` in `DATA_SOURCE_BUILDERS` (`builders/jinja_builder.py`) as `lambda sources, engine="rdflib": InMemorySPARQLDataSource(make_graph_store(Engine(engine), sources=sources).query)`; make tests pass

## 4. Concurrent-read safety & supersession coverage

- [x] 4.1 Add a test: concurrent read queries against one `from_rdf(...)` store (threads) return correct, uncorrupted results (forward-compat, DEC-7)
- [x] 4.2 Add a regression test asserting the legacy `from_rdf_file` / `RDFFileDataSource` is unchanged and still registered (supersession without removal)

## 5. Dependencies, versioning, docs, guardrails

- [x] 5.1 Add `oxigraph = ["pyoxigraph~=0.4"]` to `[project.optional-dependencies]` in `pyproject.toml`
- [x] 5.2 Bump `eds4jinja2/__init__.py` `__version__` 0.3.1 → next MINOR (additive)
- [x] 5.3 Add a changelog/README note documenting `from_rdf(sources, engine)`, the rdflib default, the opt-in `eds4jinja2[oxigraph]` extra, and that it supersedes (does not remove) `from_rdf_file`
- [x] 5.4 Run `make` checks: import-linter (`graph_store` stays innermost, no upward imports), ruff, mypy, tox (py311/py312) green; confirm ≥80% coverage on new code; confirm `pyoxigraph` is NOT pulled into the default install

## Roadmap

- [x] 1.1 · [ ] 1.2 · [ ] 1.3 · [ ] 1.4 · [ ] 1.5 · [ ] 1.6 · [ ] 2.1 · [ ] 2.2 · [ ] 2.3 · [ ] 2.4 · [ ] 3.1 · [ ] 3.2 · [ ] 3.3 · [ ] 3.4 · [ ] 4.1 · [ ] 4.2 · [ ] 5.1 · [ ] 5.2 · [ ] 5.3 · [ ] 5.4

## Verification

All unit + concurrency tests green under tox (py311/py312); import-linter/ruff/mypy clean;
the default install does NOT pull `pyoxigraph` (it is reached only via the opt-in extra and a lazy
import); the load-once test proves no per-query re-parse; tabular + tree parity is inherited from
`InMemorySPARQLDataSource` for both engines; `from_rdf_file` / `RDFFileDataSource` remain
byte-for-byte unchanged; clarity gate scores the PLAN ≥9/10.
