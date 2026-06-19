<!-- The EPIC — the shaped bet. In Meaningfy the EPIC *is* the OpenSpec proposal. -->

# EPIC: Restructure the package into the Cosmic-Python four layers

## Appetite

**Medium.** A mechanical move + import rewrite across the package, an import-linter contract set
guarding the layer direction, and a MAJOR version bump. No behaviour change, no public-API change
at the top-level `eds4jinja2` namespace, no deprecation shims.

## Why

`eds4jinja2` already has a clean dependency direction (`entrypoints > builders > adapters`,
adapters innermost), but the structure does not match the Meaningfy Cosmic-Python standard, and
three problems follow from that:

- **Models have no home.** Pure, framework-free code — the `DataSource` ABC, the `Engine` enum,
  the SPARQL-result value objects, the SPARQL query-string builder, plus pure helpers
  (`escape_latex`, the tabular utilities, the dict/collection utilities) — currently live under
  `adapters/`, mixed in with real I/O. There is no `models/` package, so domain code and
  integration code are indistinguishable.
- **`builders` is not the standard service-layer name.** The use-case orchestration layer (the
  Jinja environment builder, the report builder, the report actions, the parallel executor) is
  called `builders`, which is the only place this repo deviates from `models / adapters /
  services / entrypoints`.
- **Nothing enforces the dependency direction.** The clean direction is a convention held by
  hand; there is no import-linter contract, so a future edit can silently reverse an arrow
  (e.g. a model importing an adapter) with no guardrail to catch it.

Aligning to the company Cosmic standard puts each kind of code in its named home and lets
import-linter mechanically prevent architectural drift. The dependency direction is already
clean, so this is a **rename + extract**, not a rewrite: introduce a real `models/` package and
rename `builders/ -> services/`, then lock both with a contract.

> This EPIC **overrides the prior repo-local decision** — recorded in `CLAUDE.md` and
> `openspec/config.yaml` — to keep the `adapters / builders / entrypoints` names. That decision
> is hereby superseded; the new names are the four Cosmic layers, and both documents are updated
> as part of this change.

## Solution outline

A single, behaviour-preserving restructure in four moves:

1. **Introduce `models/`** (pure, no I/O, no frameworks), grouped into four files. Extract the
   domain/value code that currently sits under `adapters/`: the SPARQL domain (the pure query
   builder, the substitution template, the result value objects) into `models/sparql.py`; the
   `DataSource` ABC + `UnsupportedRepresentation` plus the `Engine` enum (split out of
   `graph_store`) into `models/data_source.py`; the pure text/DataFrame transforms (`escape_latex`
   + the tabular helpers) into `models/transformations.py`; and the dict/collection helpers
   (moved out of the old `adapters/__init__.py`) into `models/collections.py`.

2. **Keep `adapters/` as I/O + integration only.** The file/remote/local/in-memory SPARQL data
   sources, the graph store (ports + rdflib/oxigraph stores + factory; importing `Engine` from
   `models`), the SPARQL query-**file** reader (the I/O half of the old `sparql_query`), the
   namespace handler, the prefix.cc fetcher, and the HTTP source stay here.

3. **Rename `builders/ -> services/`** (use-case orchestration). The Jinja builder, report
   builder, parallel executor, and report-builder actions move unchanged in content, only their
   home and import paths change.

4. **Enforce the law with import-linter.** Add a `.importlinter` contract set encoding
   `entrypoints -> services -> {adapters, models}`, `adapters -> models`, `models -> nothing`;
   add `import-linter` to the dev extra and a `make check-architecture` target.

The top-level `eds4jinja2/__init__.py` re-exports are **rewritten to the new internal paths but
keep the exact same public names** — consumers importing from `eds4jinja2` see no change.

## Key decisions

- **DEC-1 (full four-layer rename+extract, not just add `models/`)**: do the complete Cosmic
  alignment — introduce `models/` **and** rename `builders/ -> services/` — rather than only
  carving out a `models/` package and leaving `builders/`. Chosen to match the company standard
  exactly and to make the import-linter contract express the canonical four-layer law.
  *(Alternative: add `models/` only — rejected, leaves the non-standard `builders` name and a
  contract that does not match the standard.)*
- **DEC-2 (pure helpers live IN `models/`, no `commons/`)**: utilities with no I/O
  (`escape_latex`, the tabular helpers, the dict/collection helpers) are domain-level pure code,
  so they go into `models/`. The text/DataFrame transforms (`escape_latex` + the tabular helpers)
  group into `models/transformations.py`; the dict/list utilities stay in `models/collections.py`
  (a distinct concern, and `invert_dict` is also a public Jinja filter shared by
  `namespace_handler` and `prefix_cc_fetcher`, so `collections.py` is a shared models home).
  *(Alternative: a separate `commons/` / `utils/` package — rejected, adds a fifth bucket outside
  the four-layer standard for code that is simply pure.)*
- **DEC-3 (split pure from I/O on the SPARQL boundary)**: the `DataSource` ABC and the SPARQL
  domain are `models`; **SPARQL query-string building is pure** (`models/sparql.py`:
  `build_query`, `is_empty_query`, `EMPTY_QUERY_ERROR`, plus the `SubstitutionTemplate` and the
  `SparqlTerm` / `SparqlResults` value objects) while **reading a query file is I/O**
  (`adapters/query_files.py`: `read_query_file`). The old `sparql_query` module is split along
  that pure/I-O seam. The `Engine` enum is a small data-source value object and lives in
  `models/data_source.py` (not a separate `engine.py`); `graph_store` imports `Engine` from
  `models.data_source`.
- **DEC-4 (dependency law enforced by import-linter)**: contracts encode
  `entrypoints -> services -> {adapters, models}`, `adapters -> models`, `models -> nothing`
  (models imports nothing upward). Add `import-linter` to the dev extra and a
  `make check-architecture` target so the law is checked locally and in CI.
- **DEC-5 (HARD BREAK on import paths; MAJOR bump 0.4.0 -> 1.0.0)**: no deprecation-shim
  modules. Only the top-level `eds4jinja2` namespace stays stable; every deep import path moves
  (including the `mkreport` CLI and the external rdf-differ consumer). Because deep import paths
  change, this is a breaking change for anyone importing internal modules → **MAJOR** bump.
- **DEC-6 (update the orientation docs)**: `CLAUDE.md` and `openspec/config.yaml` `context:`
  currently say "keep the real layer names — NOT the generic domain/services/commons folders".
  Both are updated to describe the new `models / adapters / services / entrypoints` layout, so
  the orientation index matches reality after the move.
- **DEC-7 (test files kept flat — deliberate deferral)**: test imports are updated to the new
  paths, but test files are **not** moved into per-layer subfolders in this change. Several
  tests resolve fixtures via `__file__`-relative paths (e.g.
  `Path(__file__).parent.parent / "test_data/..."`) that break when the file is relocated.
  Reorganising tests into an isomorphic per-layer tree is documented here as an explicit,
  separate follow-up.

## Rabbit-holes

- Do **not** change any behaviour. Every move is content-preserving; only module homes and
  import statements change.
- Do **not** add a `commons/` or `utils/` package — pure helpers are `models` (DEC-2).
- Do **not** write deprecation shims or re-export the old deep paths; the break is intended
  (DEC-5).
- Do **not** reorganise the test tree into per-layer subfolders in this change (DEC-7) — only
  update imports.
- Do **not** touch the data-source / result contracts or the SPARQL-JSON / tabular shapes.
- Do **not** over-fit the import-linter contract to today's module names beyond the four-layer
  direction — express the layer law, not a per-file allow-list.

## No-gos

<!-- MANDATORY. Explicitly out of scope. -->

- **No behaviour changes.** This is a pure move/rename; outputs are byte-for-byte identical.
- **No public-API change** at the top-level `eds4jinja2` namespace — every name in `__all__`
  still imports from `eds4jinja2` unchanged.
- **No deprecation-shim modules.** The deep-import break is intentional; old paths are not
  re-exported.
- **No moving of test files** into per-layer subfolders in this change (imports only).
- **No change to the data-source or result contracts**, nor to the SPARQL-JSON / tabular shapes.
- **No new runtime dependency** — `import-linter` is a dev-only addition.

---

## What Changes

- **Create `models/`** (pure), exactly four files:
  - `sparql.py` — merges `build_query` / `is_empty_query` / `EMPTY_QUERY_ERROR` (the pure part of
    the old `sparql_query`), the `SubstitutionTemplate` (from `substitution_template`), and the
    `SparqlTerm` / `SparqlResults` value objects (from `sparql_results`) — all SPARQL domain.
  - `data_source.py` — `DataSource` ABC + `UnsupportedRepresentation` (from
    `adapters/base_data_source.py`) plus the `Engine` enum (split out of `graph_store`).
  - `transformations.py` — merges `escape_latex` (from `latex_utils`) and the tabular helpers
    (`add_relative_figures`, `replace_strings_in_tabular`, from `tabular_utils`) — pure
    text/DataFrame transformations used as Jinja filters/helpers.
  - `collections.py` — `invert_dict` / `deep_update` / `first_key` / `first_key_value` /
    `sort_by_size_and_alphabet` (from the old `adapters/__init__.py`), unchanged.
- **Keep `adapters/`** (I/O): `file_ds`, `remote_sparql_ds`, `local_sparql_ds`,
  `in_memory_sparql_ds`, `graph_store` (`GraphStorePort` + Rdflib/Oxigraph stores +
  `make_graph_store`; imports `Engine` from `models`), `query_files.py` (`read_query_file` — the
  I/O half of the old `sparql_query`), `namespace_handler`, `prefix_cc_fetcher`, `http_ds`.
- **Rename `builders/ -> services/`**: `jinja_builder`, `report_builder`, `parallel_executor`,
  `report_builder_actions`.
- **`entrypoints/`**: `cli/main.py` imports updated to `services`.
- **Rewrite `eds4jinja2/__init__.py` re-exports** to the new internal paths while keeping the
  exact same public names (`__all__` unchanged).
- **Add `.importlinter`** with the four-layer contract set; add `import-linter` to the dev
  extra; add a `make check-architecture` target.
- **Update `CLAUDE.md` and `openspec/config.yaml`** `context:` to describe the new layer names.
- **Update all test imports** to the new paths (test files stay flat — DEC-7).
- **Bump version 0.4.0 -> 1.0.0** (MAJOR — breaking deep-import move).

## Capabilities

### New Capabilities
- `cosmic-layer-restructure`: the package is organised into the four Cosmic-Python layers
  `models / adapters / services / entrypoints` with the documented contents, the dependency
  direction is enforced by import-linter, the top-level public API is unchanged, and the version
  is bumped to 1.0.0 to signal the breaking deep-import move.

### Modified Capabilities
<!-- None: no existing spec carries requirements for the package's layer layout yet. -->

## Impact

- **Code**: new `eds4jinja2/models/` package; `eds4jinja2/adapters/` reduced to I/O modules
  (plus new `query_files.py`); `eds4jinja2/builders/` renamed to `eds4jinja2/services/`;
  `eds4jinja2/entrypoints/cli/main.py` import updates; `eds4jinja2/__init__.py` re-export
  rewrite. New `.importlinter`. Updated `Makefile`, `pyproject.toml` (dev extra), `CLAUDE.md`,
  `openspec/config.yaml`. All `tests/` import updates.
- **APIs**: no top-level public-API change; **all internal deep-import paths move** (breaking
  for deep-importing consumers, incl. the CLI and rdf-differ).
- **Dependencies**: `import-linter` added to the dev extra only; no runtime dependency change.
- **Version**: 0.4.0 -> 1.0.0 (MAJOR — breaking import-path move).
- **Golden thread / driver**: company Cosmic-Python standardisation — bring `eds4jinja2` onto
  the `models / adapters / services / entrypoints` layout with enforced boundaries.
