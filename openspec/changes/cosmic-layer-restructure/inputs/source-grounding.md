# Seed input — source grounding (preserved, never groomed)

Findings from reading the actual source on which the EPIC/PLAN are grounded.

## Layers today (pre-change)

- `openspec/config.yaml` `context:` and `CLAUDE.md`: real layers `entrypoints > builders >
  adapters` (adapters innermost). Both documents explicitly say "keep the real layer names —
  NOT the generic domain/services/commons folders". **This change overrides that decision**
  (DEC-1, DEC-6).
- The dependency direction is already clean (entrypoints → builders → adapters); but it is a
  hand-held convention — there is **no `.importlinter`** in the repo, so nothing enforces it.

## Pure code currently misfiled under `adapters/` (→ `models`)

- `adapters/base_data_source.py`: `DataSource` ABC — fail-safe `fetch_tabular` / `fetch_tree`
  wrappers returning `(result, error)`, four abstract methods
  (`_can_be_tabular` / `_can_be_tree` / `_fetch_tabular` / `_fetch_tree`), and
  `UnsupportedRepresentation`. Pure → `models/data_source.py` (which also gains the `Engine` enum).
- `adapters/sparql_results.py`: `SparqlTerm` / `SparqlResults` value objects. Pure →
  merged into `models/sparql.py`.
- `adapters/substitution_template.py`: `SubstitutionTemplate`. Pure →
  merged into `models/sparql.py`.
- `adapters/latex_utils.py`: `escape_latex`. Pure → merged into `models/transformations.py`.
- `adapters/tabular_utils.py`: tabular helpers incl. `add_relative_figures`,
  `replace_strings_in_tabular`. Pure → merged into `models/transformations.py`.
- `adapters/__init__.py`: dict/collection helpers — `sort_by_size_and_alphabet`, `first_key`,
  `first_key_value`, `invert_dict`, `deep_update`. Pure → `models/collections.py`
  (leaving `adapters/__init__.py` empty). `invert_dict` is also a public Jinja filter shared by
  `namespace_handler` / `prefix_cc_fetcher`, so `collections.py` stays its own shared models file.

## The pure/I-O splits

- `adapters/sparql_query.py` mixes pure string building with file I/O:
  - pure: `EMPTY_QUERY_ERROR = "The query is empty."`, `build_query(sparql_query,
    substitution_variables=None, prefixes="")`, `is_empty_query(query)` → merged into
    `models/sparql.py`.
  - I/O: `read_query_file(sparql_query_file_path)` → `adapters/query_files.py`.
- `adapters/graph_store.py`: `class Engine(str, Enum)` (L51) is pure → `models/data_source.py`. The
  rest stays in `adapters`: `GraphStorePort` (ABC, L57), `RdflibGraphStore` (L70),
  `OxigraphGraphStore` (L88), `make_graph_store(engine=Engine.RDFLIB, sources=None, graph=None)`
  (L114) — these do I/O and now import `Engine` from `models.data_source`.

## I/O modules that stay in `adapters/`

`file_ds.py`, `remote_sparql_ds.py`, `local_sparql_ds.py` (RDFFileDataSource),
`in_memory_sparql_ds.py` (InMemorySPARQLDataSource), `graph_store.py`, `namespace_handler.py`
(NamespaceInventory), `prefix_cc_fetcher.py`, `http_ds.py`, and the new `query_files.py`.

## Service layer (renamed `builders/ -> services/`)

`builders/jinja_builder.py` (build_eds_environment, inject_environment_globals,
DATA_SOURCE_BUILDERS, TABULAR_HELPERS, TREE_HELPERS, ADDITIONAL_FILTERS),
`builders/report_builder.py`, `builders/parallel_executor.py`,
`builders/report_builder_actions.py` → `services/…` (content unchanged).

## Public API + version

- `eds4jinja2/__init__.py` re-exports public names from deep paths and currently pulls from
  `adapters.tabular_utils` and `builders.jinja_builder`. `__all__` =
  `build_eds_environment`, `inject_environment_globals`, `FileDataSource`,
  `RemoteSPARQLEndpointDataSource`, `RDFFileDataSource`, `InMemorySPARQLDataSource`,
  `make_graph_store`, `RdflibGraphStore`, `OxigraphGraphStore`, `Engine`, `add_relative_figures`,
  `replace_strings_in_tabular`, `NamespaceInventory`. Re-exports are rewritten to the new layer
  paths; the public names and `__all__` stay identical (DEC-5 / public-API stability).
- Version single source of truth is the **`eds4jinja2/VERSION` file** (read by `__init__.py`
  via `pathlib`, by `pyproject.toml` `[tool.setuptools.dynamic]`, and by `docs/conf.py`).
  Currently `0.4.0`. Bump → `1.0.0` (MAJOR — breaking deep-import move).
  *(Note: `CLAUDE.md` still describes the SoT as `__init__.py:__version__`; the live SoT is the
  `VERSION` file — the docs update should reflect this.)*

## Constraints

- Python 3.11/3.12; pip + tox + `pyproject.toml` (setuptools backend, NOT Poetry); `make` is the
  dev/CI interface; default branch `master`.
- `import-linter` is a **dev-only** addition; no runtime dependency change.

## Deliberate deferral (DEC-7)

Test files are NOT moved into per-layer subfolders in this change — several use
`Path(__file__).parent.parent / "test_data/..."` fixture lookups that break on relocation. Only
test imports are updated. Per-layer test reorganisation is a documented follow-up.

## Driver / golden thread

Company Cosmic-Python standardisation: bring `eds4jinja2` onto the
`models / adapters / services / entrypoints` layout with import-linter-enforced boundaries,
overriding the prior repo-local decision to keep `adapters / builders / entrypoints`.
