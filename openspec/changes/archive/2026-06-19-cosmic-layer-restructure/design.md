<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Parent: EPIC `cosmic-layer-restructure` (proposal.md) — derived from DEC-1..DEC-7.

## Context

`eds4jinja2` is a library that embeds data-source specifications (RDF/SPARQL endpoints, tabular
files) into Jinja2 templates to drive report generation. The package today has three real
layers with a clean dependency direction:

```
entrypoints (CLI mkreport)
   └─> builders   (jinja_builder, report_builder, report_builder_actions, parallel_executor)
          └─> adapters  (file_ds, remote/local/in_memory sparql, graph_store, namespace_handler,
                         prefix_cc_fetcher, http_ds, base_data_source, sparql_query/results,
                         substitution_template, latex_utils, tabular_utils, collection helpers
                         in adapters/__init__.py)
```

The direction is clean, but two things are off relative to the Meaningfy Cosmic standard:

1. **`adapters/` is doing two jobs.** It holds genuine I/O (HTTP, file reads, SPARQL endpoints,
   graph stores) **and** pure, framework-free code that has no business in an adapters layer —
   the `DataSource` ABC, the `Engine` enum (currently inside `graph_store.py`), the SPARQL-result
   value objects, the pure SPARQL query-string builder, the substitution template, and pure
   helpers (`latex_utils`, `tabular_utils`, the dict helpers in `adapters/__init__.py`).
2. **`builders/` is the non-standard name** for the service / use-case layer.

Nothing enforces the direction; it is a hand-held convention with no `.importlinter`.

Grounding (verified against the source):
- `adapters/base_data_source.py` — `DataSource` ABC (fail-safe `fetch_tabular` / `fetch_tree`
  wrappers + four abstract methods) and `UnsupportedRepresentation`. **Pure → `models`.**
- `adapters/graph_store.py` — `Engine(str, Enum)` at L51, then `GraphStorePort` (ABC),
  `RdflibGraphStore`, `OxigraphGraphStore`, and `make_graph_store(engine, sources, graph)`.
  **`Engine` is pure → `models/data_source.py`; the stores + factory are I/O → stay in
  `adapters`, importing `Engine` from `models.data_source`.**
- `adapters/sparql_query.py` — mixes pure string building (`build_query`, `is_empty_query`,
  `EMPTY_QUERY_ERROR`) with file reading (`read_query_file`). **Split on the pure/I-O seam:
  pure → `models/sparql.py`; `read_query_file` → `adapters/query_files.py`.**
- `adapters/sparql_results.py` + `adapters/substitution_template.py` — pure SPARQL domain.
  **→ merged into `models/sparql.py`** (alongside the pure query builder).
- `adapters/latex_utils.py` + `adapters/tabular_utils.py` — pure text/DataFrame transforms.
  **→ merged into `models/transformations.py`.**
- the dict helpers in `adapters/__init__.py` (`sort_by_size_and_alphabet`, `first_key`,
  `first_key_value`, `invert_dict`, `deep_update`) — all pure. **→ `models/collections.py`.**
- `eds4jinja2/__init__.py` re-exports public names from deep paths
  (`adapters.tabular_utils`, `builders.jinja_builder`, …). **Re-exports rewritten to new paths;
  public names unchanged.**
- Version single source of truth is the `eds4jinja2/VERSION` file (read by `__init__.py`,
  `pyproject.toml` `[tool.setuptools.dynamic]`, and `docs/conf.py`). Currently `0.4.0`.

**Constraints**: Python 3.11/3.12; pip + tox + `pyproject.toml` (setuptools backend, NOT Poetry);
`make` is the dev/CI interface; default branch `master`.

## Goals / Non-Goals

**Goals:**
- Organise the package into `models / adapters / services / entrypoints` with the documented
  contents (DEC-1, DEC-2, DEC-3).
- Enforce `entrypoints -> services -> {adapters, models}`, `adapters -> models`,
  `models -> nothing` with import-linter and a `make check-architecture` target (DEC-4).
- Keep the top-level `eds4jinja2` public API byte-stable (no consumer at the package namespace
  is affected).
- Bump to 1.0.0 to signal the breaking deep-import move (DEC-5).
- Update the orientation docs to the new layout (DEC-6).

**Non-Goals:**
- No behaviour change of any kind (pure move/rename).
- No public-API change at the `eds4jinja2` namespace.
- No deprecation shims / old-path re-exports.
- No per-layer reorganisation of the test tree (imports only — DEC-7).
- No change to data-source / result contracts or output shapes.

## Decisions

- **DEC-1 (full rename+extract)**: introduce `models/` and rename `builders/ -> services/` in
  one change, so the contract can express the canonical four-layer law. *(Alt: add `models/`
  only — rejected, leaves the non-standard `builders` name.)*
- **DEC-2 (pure helpers in `models/`)**: pure transforms (`escape_latex` + the tabular helpers)
  live in `models/transformations.py`; the dict/list utilities stay in `models/collections.py`
  (a distinct concern, and `invert_dict` is also a public Jinja filter shared by
  `namespace_handler` / `prefix_cc_fetcher`). No `commons/` package. *(Alt: a `commons/` bucket —
  rejected, a fifth bucket for code that is simply pure.)*
- **DEC-3 (pure/I-O split on the SPARQL boundary)**: `models/sparql.py` holds `build_query`,
  `is_empty_query`, `EMPTY_QUERY_ERROR` (plus the `SubstitutionTemplate` and the `SparqlTerm` /
  `SparqlResults` value objects); `adapters/query_files.py` holds `read_query_file`. The `Engine`
  enum → `models/data_source.py` (not a separate `engine.py`); `graph_store.py` (stores +
  factory) stays in `adapters` and imports `Engine` from `models.data_source`.
- **DEC-4 (import-linter law)**: a layered contract with `models` lowest and `entrypoints`
  highest, plus independence/forbidden rules so `models` imports nothing from the other three
  layers and `adapters` imports nothing from `services` / `entrypoints`. `make
  check-architecture` runs `lint-imports`; `import-linter` is in the dev extra; CI runs the
  target.
- **DEC-5 (hard break, MAJOR bump)**: no shims. `eds4jinja2/VERSION` goes `0.4.0 -> 1.0.0`;
  `__init__.py`, `pyproject.toml`, and `docs/conf.py` already read that file, so the bump is a
  one-line edit.
- **DEC-6 (docs)**: rewrite the `Architecture:` line in `openspec/config.yaml` `context:` and
  the "Real layers (verified)" / "Layers / modules" notes in `CLAUDE.md` to the new
  `models / adapters / services / entrypoints` layout.
- **DEC-7 (flat tests)**: update test imports only; do not relocate test files (several use
  `Path(__file__).parent.parent / "test_data/..."`, which breaks on relocation). Per-layer test
  reorganisation is a documented follow-up, out of scope here.

## Target structure

```
eds4jinja2/
├── __init__.py            # public re-exports → new paths, SAME public names (__all__ stable)
├── VERSION                # 1.0.0
├── models/                # PURE: no I/O, no frameworks; imports nothing upward (4 files)
│   ├── sparql.py                  # build_query, is_empty_query, EMPTY_QUERY_ERROR,
│   │                              #   SubstitutionTemplate, SparqlTerm, SparqlResults
│   ├── data_source.py             # DataSource ABC + UnsupportedRepresentation + Engine enum
│   ├── transformations.py         # escape_latex, add_relative_figures,
│   │                              #   replace_strings_in_tabular
│   └── collections.py             # invert_dict, deep_update, first_key, first_key_value,
│                                  #   sort_by_size_and_alphabet
├── adapters/              # I/O + integration; imports only models
│   ├── file_ds.py
│   ├── remote_sparql_ds.py
│   ├── local_sparql_ds.py
│   ├── in_memory_sparql_ds.py
│   ├── graph_store.py             # GraphStorePort + Rdflib/Oxigraph stores + make_graph_store
│   │                              #   (imports Engine from models)
│   ├── query_files.py             # read_query_file (I/O half of the old sparql_query)
│   ├── namespace_handler.py
│   ├── prefix_cc_fetcher.py
│   └── http_ds.py
├── services/             # use-case orchestration (renamed from builders/);
│   │                     #   imports adapters + models
│   ├── jinja_builder.py
│   ├── report_builder.py
│   ├── parallel_executor.py
│   └── report_builder_actions.py
└── entrypoints/          # CLI; imports services
    └── cli/main.py
```

## Algorithm / approach

This is a mechanical, content-preserving restructure. Order matters to keep the tree importable
between steps and to make the import-linter contract green only once the moves are done.

1. **Extract `models/` (pure), merging into four files.** Move the pure code out of `adapters/`:
   `base_data_source.py -> models/data_source.py`; `latex_utils.py` + `tabular_utils.py` merge
   into `models/transformations.py`; the dict helpers from `adapters/__init__.py ->
   models/collections.py`; and `sparql_results.py` + `substitution_template.py` merge into
   `models/sparql.py` (alongside the pure query builder from step 2).
2. **Split the SPARQL modules + fold in `Engine`.** From the old `sparql_query.py`, put
   `build_query`, `is_empty_query`, `EMPTY_QUERY_ERROR` into `models/sparql.py` (joining the
   substitution template and result value objects from step 1), and `read_query_file` into
   `adapters/query_files.py`. Split `Engine` out of `graph_store.py` into `models/data_source.py`;
   `graph_store.py` keeps the stores + factory and imports `Engine` from `models.data_source`.
3. **Rename `builders/ -> services/`** (four modules, content unchanged).
4. **Rewrite imports everywhere**: adapters now import pure code from `models`; services import
   from `adapters` + `models`; the CLI imports from `services`; `__init__.py` re-exports from the
   new paths with the **same public names**.
5. **Add `.importlinter`** (contract below) + dev-extra entry + `make check-architecture`.
6. **Bump `VERSION` 0.4.0 -> 1.0.0.**
7. **Update `CLAUDE.md` + `openspec/config.yaml`** to the new layout.
8. **Update test imports** (files stay flat).

**Import-linter contract (`.importlinter`):**
```ini
[importlinter]
root_package = eds4jinja2

[importlinter:contract:layers]
name = eds4jinja2 cosmic layers
type = layers
layers =
    eds4jinja2.entrypoints
    eds4jinja2.services
    eds4jinja2.adapters
    eds4jinja2.models

[importlinter:contract:models-are-pure]
name = models import nothing upward
type = forbidden
source_modules =
    eds4jinja2.models
forbidden_modules =
    eds4jinja2.adapters
    eds4jinja2.services
    eds4jinja2.entrypoints

[importlinter:contract:adapters-only-models]
name = adapters import nothing above adapters
type = forbidden
source_modules =
    eds4jinja2.adapters
forbidden_modules =
    eds4jinja2.services
    eds4jinja2.entrypoints
```
The `layers` contract gives the top-level direction; the two `forbidden` contracts make the
critical "models pure" and "adapters do not reach up" rules explicit and self-documenting.

**`make` target:**
```make
check-architecture:
	lint-imports
```

**Public re-export rewrite (`eds4jinja2/__init__.py`) — names unchanged:**
```python
from eds4jinja2.adapters.file_ds import FileDataSource
from eds4jinja2.adapters.graph_store import make_graph_store, RdflibGraphStore, OxigraphGraphStore
from eds4jinja2.models.data_source import Engine
from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource
from eds4jinja2.adapters.local_sparql_ds import RDFFileDataSource
from eds4jinja2.adapters.namespace_handler import NamespaceInventory
from eds4jinja2.adapters.remote_sparql_ds import RemoteSPARQLEndpointDataSource
from eds4jinja2.models.transformations import add_relative_figures, replace_strings_in_tabular
from eds4jinja2.services.jinja_builder import build_eds_environment, inject_environment_globals
# __all__ is identical to the pre-change set.
```

### Anti-patterns
- ❌ Leaving pure code (`DataSource` ABC, `Engine`, query string builder, helpers) in
  `adapters/` — that is the whole reason for the change.
- ❌ Adding a `commons/` / `utils/` package for pure helpers (DEC-2: they are `models`).
- ❌ Writing deprecation shims or re-exporting old deep paths (DEC-5: the break is intended).
- ❌ Importing `Engine` from `adapters.graph_store` after the split — it now lives in
  `models.data_source` (re-export from `graph_store` only if a sibling already imports it there;
  the public name comes from `__init__`).
- ❌ A model importing an adapter or a service — the import-linter contract must fail this.
- ❌ Moving test files into per-layer subfolders (DEC-7: imports only).
- ❌ Hand-editing a version literal — `VERSION` is the single source of truth.

## Error matrix

| Failure mode | Expected handling |
|---|---|
| A model imports an adapter/service/entrypoint | `lint-imports` fails the `models-are-pure` contract; `make check-architecture` exits non-zero |
| An adapter imports a service/entrypoint | `lint-imports` fails the `adapters-only-models` contract |
| Layer order violated (e.g. adapter imports service) | `lint-imports` fails the `layers` contract |
| A deep-import consumer uses an old path (e.g. `eds4jinja2.builders.report_builder`) | `ImportError` — intended hard break (DEC-5); the consumer migrates to `eds4jinja2.services.report_builder` or the top-level re-export |
| A top-level public name is dropped or moved | caught by the public-API stability tests (the previously-exported names must still import from `eds4jinja2`) |
| `VERSION` not bumped | the version test asserts `1.0.0`; build/release reads the stale value |
| A test still imports an old path after the move | that test's collection fails on import (caught by tox) |

## Risks / Trade-offs

- **[Public-API regression during the re-export rewrite]** → Mitigation: a test imports every
  name in the pre-change `__all__` from `eds4jinja2` and asserts they resolve; `__all__` is
  asserted unchanged.
- **[A pure module silently retains an I/O import after extraction]** (e.g. `models/sparql.py`
  still importing the file reader) → Mitigation: the `models-are-pure` contract + a unit import of
  each `models` module with no adapter on the path.
- **[Deep-import consumers break unexpectedly]** → Mitigation: this is intentional (DEC-5) and
  signalled by the MAJOR bump; the changelog/release notes list the moved paths and their new
  homes (CLI and rdf-differ called out).
- **[`__file__`-relative test fixtures break if tests are moved]** → Mitigation: DEC-7 keeps
  tests flat; only imports change, so fixture paths are untouched.
- **[Orientation docs drift from reality]** → Mitigation: DEC-6 updates `CLAUDE.md` and
  `openspec/config.yaml` in the same change.

## Open Questions

- Whether to later add a `forbidden` contract pinning each *module* to its layer (beyond the
  layer-level rule) — parked; the layer + two forbidden contracts already cover the law, and a
  per-module allow-list would be brittle to future additions.
- Per-layer reorganisation of the test tree (isomorphic to the package) — deferred (DEC-7);
  blocked on replacing `__file__`-relative fixture lookups with a fixtures helper. Tracked as a
  follow-up change.
