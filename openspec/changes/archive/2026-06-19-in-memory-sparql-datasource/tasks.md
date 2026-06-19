<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [x]` checkboxes. -->

> Derived from EPIC `in-memory-sparql-datasource` (proposal.md)  <!-- cite your parent (golden thread) -->

## 1. InMemorySPARQLDataSource (TDD: tests first)

- [x] 1.1 Write failing unit tests `tests/unit/test_in_memory_sparql_ds.py`: tabular fetch from an `rdflib.Graph` returns a `pd.DataFrame` with stringified bindings (assert columns + cell values)
- [x] 1.2 Add failing tests for tabular fetch via a `query(sparql_text)` callable (pyoxigraph-style stub) producing the same DataFrame shape
- [x] 1.3 Add failing tests for `_fetch_tree` returning the SPARQL-JSON dict shape (`head.vars`, `results.bindings` with `type`/`value`; datatype + lang carried) for both rdflib.Graph and callable inputs
- [x] 1.4 Add failing tests for edge/error cases: empty query → `Exception`, empty result set → empty DataFrame / empty bindings, invalid `source` → `TypeError`
- [x] 1.5 Implement `eds4jinja2/adapters/in_memory_sparql_ds.py` — `InMemorySPARQLDataSource(DataSource)` with `__init__` (Graph-or-callable), `with_query`, `_fetch_tabular`, `_fetch_tree`, `_can_be_tabular`/`_can_be_tree`, `__str__`; module constants for SPARQL-JSON keys and term types; make tests pass

## 2. ReportBuilder builder-injection seam (TDD)

- [x] 2.1 Write failing unit test in `tests/unit/test_report_builder.py`: constructing `ReportBuilder` with `external_data_source_builders={"from_endpoint": ...}` overrides the registered builder in `template_env.globals`
- [x] 2.2 Write failing backward-compat test: constructing `ReportBuilder` with NO new kwargs leaves the default globals/filters intact (`from_file`, `invert_dict`, `escape_latex` present)
- [x] 2.3 Write failing test: injecting only `from_endpoint` still preserves the default helper globals (merge-over-defaults, DEC-1 caveat)
- [x] 2.4 Implement the seam in `builders/report_builder.py` — add `external_data_source_builders={}` / `external_filters={}` kwargs, merge over `DATA_SOURCE_BUILDERS`/`TABULAR_HELPERS`/`TREE_HELPERS` and `ADDITIONAL_FILTERS`, forward to `build_eds_environment`; make tests pass

## 3. Optional explicit registration

- [x] 3.1 Write failing `tests/unit/test_jinja_builder.py` assertion that `from_graph` (alias `from_memory`) is in `DATA_SOURCE_BUILDERS` and builds an `InMemorySPARQLDataSource`
- [x] 3.2 Register `from_graph` / `from_memory` in `DATA_SOURCE_BUILDERS` (`builders/jinja_builder.py`); make tests pass

## 4. Parity & integration coverage

- [x] 4.1 Add a parity test asserting the in-memory tree dict structure matches the documented `RemoteSPARQLEndpointDataSource` SPARQL-JSON shape (keys + nesting)
- [x] 4.2 Add an end-to-end test: render a small report through `ReportBuilder` with `from_endpoint` overridden to `InMemorySPARQLDataSource`, templates unchanged, asserting output content

## 5. Versioning, docs, guardrails

- [x] 5.1 Bump `eds4jinja2/__init__.py` `__version__` 0.3.1 → 0.4.0 (MINOR)
- [x] 5.2 Add a changelog/README note documenting the consumer pattern (override `from_endpoint`, templates untouched) and the new adapter
- [x] 5.3 Run `make` checks: import-linter (adapter stays innermost), ruff, mypy, tox (py311/py312) green; confirm ≥80% coverage on new code

## Roadmap

- [x] 1.1 · [ ] 1.2 · [ ] 1.3 · [ ] 1.4 · [ ] 1.5 · [ ] 2.1 · [ ] 2.2 · [ ] 2.3 · [ ] 2.4 · [ ] 3.1 · [ ] 3.2 · [ ] 4.1 · [ ] 4.2 · [ ] 5.1 · [ ] 5.2 · [ ] 5.3

## Verification

All unit + parity + e2e tests green under tox (py311/py312); import-linter/ruff/mypy clean;
backward-compat test proves no-kwarg `ReportBuilder` is unchanged; templates remain byte-for-byte
unchanged; clarity gate scores the PLAN ≥9/10.
