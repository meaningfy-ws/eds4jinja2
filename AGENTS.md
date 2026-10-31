<!-- meaningfy-template-version: 3.0.0 -->
<!-- CANONICAL, CLI-agnostic agent instruction file (opencode reads AGENTS.md natively; Claude Code
     reads it through the @AGENTS.md import in CLAUDE.md). Edit THIS file. CLAUDE.md is a thin
     pointer that adds only Claude-specific guidance — never a symlink, never a copy. This file
     ROUTES to skills and to the global standard; it never restates that standard. -->

# Project: eds4jinja2

Meaningfy project. A library that embeds data-source specifications (RDF/SPARQL endpoints and
tabular files) directly into Jinja2 templates to drive dynamic report generation. PyPI package
with a `mkreport` CLI. The company-wide standard lives in your **global agent instructions** (`~/.claude/CLAUDE.md`) —
this file routes to it and to the installed skills, and records only what is specific to **this**
repo.

## Skill routing (use the skill for the task)

- Structuring Python code (layers, SOLID) → **cosmic-python**
- Keeping code minimal — YAGNI, simplest working approach → **ponytail**
- System / solution design (C4, ADRs, contracts) → **architecture**
- Any new feature or non-trivial change → **superpowers:brainstorming** first
- Any feature or bugfix implementation → **superpowers:test-driven-development** (tests first)
- Debugging → **superpowers:systematic-debugging**
- Shaping an EPIC + deriving its PLAN → **epic-planning** + the **`/opsx:*`** commands
- Spec readiness (PLAN clarity gate, ≥9/10) → **clarity-gate**
- BDD features → **bdd-gherkin**
- Commits / branches / PRs → **meaningfy-git-workflow** (mechanics via **commit-commands**)
- Pre-PR review → **meaningfy-code-review** (+ external **code-review**)
- Docs → **technical-writing**

If a request conflicts with these, flag it before proceeding.

## The spine — where work is shaped and remembered

This repo carries the Meaningfy **spine** under `openspec/` (OpenSpec, schema `meaningfy`):

- **EPIC ≡ `openspec/changes/<id>/proposal.md`** (Shape-Up work shape).
- **PLAN ≡ `openspec/changes/<id>/design.md` + `tasks.md`** (clarity gate scores the pair ≥9/10).
- **Normative requirements ≡ `openspec/changes/<id>/specs/<cap>/spec.md`** (RFC-2119 SHALL +
  Given/When/Then). They merge into **`openspec/specs/`** — the durable truth — on archive.
- **Orientation** is `openspec/config.yaml`'s `context:` field. The truth is `openspec/specs/`.

Drive it with the `/opsx:*` commands; they require `npx -y @fission-ai/openspec@1.4.1 init` once.

**Golden thread (cite your parent).** The PLAN cites its EPIC id; specs cite their capability;
commits reference the change.

## Working conventions

- **Cosmic-Python layers** (enforced by import-linter): `entrypoints → services → adapters →
  models`. `models` is pure (no I/O, imports nothing upward); `adapters` does I/O and imports only
  `models`; `services` orchestrates (`adapters` + `models`); `entrypoints` (CLI `mkreport`) drives
  `services`. Boundaries are checked by `make check-architecture` (`.importlinter`). *(This
  supersedes the earlier `adapters/builders/entrypoints` layout — see the archived
  `cosmic-layer-restructure` change.)*
- **Tooling is Poetry** (`poetry-core` backend, committed `poetry.lock`, PEP 735 dependency
  groups `test` and `lint`); no tox. Tool config lives in root files: `ruff.toml`, `mypy.ini`,
  `pytest.ini`, `.coveragerc`, `.importlinter`. The `make` targets are the dev/CI interface:
  `make install`, `make check-all` (the gate CI runs: `check-version`, `lint`, `typecheck`,
  `check-architecture`, `check-spec`, `test`), `make test-unit`, `make test-features`,
  `make test-network`, `make build`.
- Target interpreters: **Python 3.12, 3.13 and 3.14** (`requires-python >=3.12`).
- Runtime dependencies use major-version ranges (`>=X.Y,<X+1`); `test`/`lint` groups are pinned `==`.
- The package version is the single source of truth in the `eds4jinja2/VERSION` file
  (`eds4jinja2/__init__.py` reads it at runtime). `pyproject.toml` carries a static copy that
  `make check-version` keeps in sync.
- Tests: `tests/unit/` (unit) and `tests/steps/` + `tests/features/` (BDD). Some SPARQL tests hit
  live remote endpoints and need network; `test_describe_uri` asserts on remote data that can
  drift.
- **GitFlow** (meaningfy-git-workflow, meaningfy-release). Two long-lived branches, never committed
  to directly:
  - **`develop`** — integration. `feature/<descriptor>` branches off it and returns by PR into it.
  - **`master`** — released history only; every merge into it is a release, tagged `X.Y.Z` (no `v`
    prefix, as `2.0.0`–`2.1.1`). The docs site deploys from `master`, so it shows released docs.
  - **Release:** cut `release/X.Y.Z` from `develop` (version bump in `eds4jinja2/VERSION` +
    `pyproject.toml`, CHANGELOG section, stabilisation fixes only) → PR into `master` → merge → GitHub
    Release `X.Y.Z` on the merge commit with the CHANGELOG section as notes (this runs `publish.yml`,
    PyPI Trusted Publishing) → merge `master` back into `develop`.
  - **Hotfix:** cut `hotfix/X.Y.Z` from the released tag → PR into `master` → release as above →
    merge back into `develop`.
  - CI: `main.yml` runs on pull requests to and pushes on both lines; the docs build runs on pull
    requests to both lines and deploys only on pushes to `master`.

## `.claude/` is a regenerable index — the truth is `openspec/specs/`

`.claude/memory/MEMORY.md` is a cheap orientation note (≤200 lines; stable patterns only). It is
an **index, not authority** — if it disagrees with `openspec/specs/`, `specs/` wins.

## Project specifics

- **Archetype:** library (pip-installable; published to PyPI; CLI entrypoint `mkreport`).
- **Top-level package:** `eds4jinja2/` (no `/src`).
- **Layers / modules:** `models` (pure domain: `sparql` query+results, `data_source` ABC+`Engine`,
  `transformations` latex/tabular, `collections` dict utils), `adapters` (I/O data sources: file,
  local/remote/in-memory SPARQL, graph store, namespaces, query files), `services` (Jinja env +
  report builder + actions + parallel executor), `entrypoints` (CLI).
- **Datastores / external systems:** SPARQL endpoints (remote + local rdflib), Fuseki for tests
  (`make start-fuseki`), tabular files (csv/tsv/xls/xlsx via pandas).
- **Deployable?** No — it is a library.

Documentation lives in `docs/` as **AsciiDoc, built by Antora** (not Sphinx). Build/preview locally
with `make build-docs` / `make preview-docs` (needs Node.js); a GitHub Actions workflow
(`.github/workflows/docs.yml`) builds on every PR and deploys to **GitHub Pages**
(https://meaningfy-ws.github.io/eds4jinja2/). ReadTheDocs is not used.
