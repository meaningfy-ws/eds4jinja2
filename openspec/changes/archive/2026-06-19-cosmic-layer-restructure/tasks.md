<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [x]` checkboxes. -->

> Derived from EPIC `cosmic-layer-restructure` (proposal.md)  <!-- cite your parent (golden thread) -->

## 1. Extract the `models/` package (pure code — 4 files)

- [x] 1.1 Create `eds4jinja2/models/__init__.py`
- [x] 1.2 Create `models/data_source.py` by moving `adapters/base_data_source.py` (`DataSource` ABC + `UnsupportedRepresentation`), content unchanged
- [x] 1.3 Create `models/transformations.py` by merging `adapters/latex_utils.py` (`escape_latex`) and `adapters/tabular_utils.py` (`add_relative_figures`, `replace_strings_in_tabular`)
- [x] 1.4 Create `models/collections.py` by moving the dict helpers from `adapters/__init__.py` (`invert_dict`, `deep_update`, `first_key`, `first_key_value`, `sort_by_size_and_alphabet`); leave `adapters/__init__.py` empty
- [x] 1.5 Start `models/sparql.py` by merging `adapters/sparql_results.py` (`SparqlTerm`, `SparqlResults`) and `adapters/substitution_template.py` (`SubstitutionTemplate`) — the pure query builder is folded in at task 2.1

## 2. Split the SPARQL + engine modules on the pure/I-O seam

- [x] 2.1 Fold the pure part of the old `sparql_query` (`build_query`, `is_empty_query`, `EMPTY_QUERY_ERROR`) into `models/sparql.py` (joining the substitution template + result value objects from task 1.5)
- [x] 2.2 Create `adapters/query_files.py` with `read_query_file` (the I/O half of the old `sparql_query`); import `build_query`/`is_empty_query` from `models.sparql` where needed
- [x] 2.3 Split `Engine(str, Enum)` out of `adapters/graph_store.py` into `models/data_source.py` (alongside the `DataSource` ABC)
- [x] 2.4 Update `adapters/graph_store.py` (keeps `GraphStorePort` + Rdflib/Oxigraph stores + `make_graph_store`) to import `Engine` from `models.data_source`

## 3. Rename `builders/ -> services/`

- [x] 3.1 Move `builders/jinja_builder.py -> services/jinja_builder.py`
- [x] 3.2 Move `builders/report_builder.py -> services/report_builder.py`
- [x] 3.3 Move `builders/parallel_executor.py -> services/parallel_executor.py`
- [x] 3.4 Move `builders/report_builder_actions.py -> services/report_builder_actions.py`
- [x] 3.5 Move `builders/__init__.py -> services/__init__.py`; remove the empty `builders/` package

## 4. Rewrite imports across the package

- [x] 4.1 Update `adapters/*` to import pure code from `models` (the `DataSource` ABC + `Engine` from `models.data_source`; the query builder / substitution template / result value objects from `models.sparql`; transforms from `models.transformations`; helpers from `models.collections`)
- [x] 4.2 Update `services/*` to import from `adapters` + `models` (e.g. `jinja_builder` registering data-source builders and tabular/latex helpers)
- [x] 4.3 Update `entrypoints/cli/main.py` to import the report builder from `services`
- [x] 4.4 Rewrite `eds4jinja2/__init__.py` re-exports to the new internal paths, keeping every public name and `__all__` identical to the pre-change set

## 5. Enforce the dependency law (import-linter)

- [x] 5.1 Add `.importlinter` with the `layers` contract (`entrypoints > services > adapters > models`) plus `forbidden` contracts (`models` import nothing upward; `adapters` import nothing above adapters)
- [x] 5.2 Add `import-linter` to the dev extra in `pyproject.toml`
- [x] 5.3 Add a `make check-architecture` target running `lint-imports`; wire it into the CI checks
- [x] 5.4 Run `make check-architecture` and confirm all contracts pass on the restructured tree

## 6. Versioning + orientation docs

- [x] 6.1 Bump `eds4jinja2/VERSION` 0.4.0 -> 1.0.0 (MAJOR — breaking deep-import move); confirm `__init__.py`, `pyproject.toml`, and `docs/conf.py` read the new value
- [x] 6.2 Update `openspec/config.yaml` `context:` `Architecture:` line to the new `models / adapters / services / entrypoints` layout
- [x] 6.3 Update `CLAUDE.md` ("Real layers (verified)" + "Layers / modules") to describe the new four-layer layout, noting it overrides the prior `adapters/builders/entrypoints` decision
- [x] 6.4 Add a changelog / release-notes note listing the moved deep-import paths and their new homes (CLI and rdf-differ consumer called out), with the 1.0.0 breaking marker

## 7. Tests (imports only — files stay flat)

- [x] 7.1 Update all `tests/unit/` imports to the new layer paths; do NOT move test files (DEC-7: `__file__`-relative fixtures would break)
- [x] 7.2 Update `tests/steps/` imports to the new layer paths
- [x] 7.3 Add a public-API stability test: every name in the pre-change `__all__` still imports from `eds4jinja2`, and `__all__` is unchanged
- [x] 7.4 Add a layer-import smoke test: each `models` module imports cleanly with no adapter/service/entrypoint on its import path
- [x] 7.5 Add a version test asserting `eds4jinja2.__version__ == "1.0.0"`

## 8. Full verification

- [x] 8.1 Run `make test-all` (tox py311/py312) green
- [x] 8.2 Run `make check-architecture` green (all import-linter contracts pass; a deliberate model→adapter import is shown to fail the contract)
- [x] 8.3 Run `make build` and confirm the wheel/sdist build with version 1.0.0
- [x] 8.4 Confirm clarity gate scores the PLAN ≥9/10

## Roadmap

- [x] 1.1 · [ ] 1.2 · [ ] 1.3 · [ ] 1.4 · [ ] 1.5 · [ ] 2.1 · [ ] 2.2 · [ ] 2.3 · [ ] 2.4 · [ ] 3.1 · [ ] 3.2 · [ ] 3.3 · [ ] 3.4 · [ ] 3.5 · [ ] 4.1 · [ ] 4.2 · [ ] 4.3 · [ ] 4.4 · [ ] 5.1 · [ ] 5.2 · [ ] 5.3 · [ ] 5.4 · [ ] 6.1 · [ ] 6.2 · [ ] 6.3 · [ ] 6.4 · [ ] 7.1 · [ ] 7.2 · [ ] 7.3 · [ ] 7.4 · [ ] 7.5 · [ ] 8.1 · [ ] 8.2 · [ ] 8.3 · [ ] 8.4

## Verification

The package imports cleanly under the four-layer layout; `make test-all` is green on py311/py312;
`make check-architecture` passes all import-linter contracts and a deliberate forbidden import is
shown to fail; the top-level `eds4jinja2` public API (every `__all__` name) is unchanged;
`eds4jinja2.__version__ == "1.0.0"`; `CLAUDE.md` and `openspec/config.yaml` describe the new
layout; test files remain flat (imports only); clarity gate scores the PLAN ≥9/10.
