# EPIC: Modernize eds4jinja2 — Meaningfy alignment, Poetry, Python 3.12+, latest dependencies

## Appetite

**LARGE.** Several related capabilities move at once: the build system (pip+tox → Poetry), the
quality gates (Ruff, mypy, coverage, spine validation, architecture in CI), the supported runtimes
(3.12–3.14) and every dependency to its latest major. Existing artifacts migrate (`tox.ini`,
`pyproject.toml`, CI workflows, agent files, memory index). Delivered in staged slices, one PR each.

## Why

The library was last packaged for Python 3.11/3.12 on dependency pins from 2023 (numpy 1.26,
pandas 2.2, pytest 7, pytest-bdd 7), and it diverges from the Meaningfy library standard in ways
that let regressions through silently: no lint or type check runs, coverage has no floor, layer
boundaries are only checked at release time, and the spine schema was a stale snapshot. A serious
dependency upgrade without those gates would be flying blind, so the gates land first and the
upgrade lands behind them. Audit: `inputs/audit-and-seeds.md`.

## Solution outline

Three stages, in this order, each leaving `make check-all` green:

1. **Spine and agent files.** Pinned `meaningfy` schema refreshed to skillery 3.7.0 (done at the
   start of this change); `AGENTS.md` becomes the canonical agent file with a thin `CLAUDE.md`
   pointer; the memory index is regenerated to match the code.
2. **Gates before upgrade.** Poetry replaces pip+tox; tool config moves to dedicated root files;
   Ruff, mypy, `openspec validate --strict` and the import-linter contracts are
   all wired into one `make check-all` that PR CI runs. The import-linter contracts are re-derived
   from the code and tightened where the code already allows it. `SECURITY.md` is added.
3. **The upgrade.** `requires-python >=3.12`; every dependency to its latest stable major; stale
   dependencies pruned; breakage fixed; CI matrix 3.12/3.13/3.14; release as **2.0.0**.

Outcome: a contributor gets one command (`make check-all`) that proves the library builds,
installs, is lint/type/architecture clean and passes its tests on every supported Python, and the
same command gates every PR.

## Key decisions

- **DEC-1**: Migrate to **Poetry** (PEP 621 `[project]` + Poetry build backend, `poetry.lock`
  committed, dependency groups for test/dev). — Aligns with the Meaningfy standard and gives a lock
  file; rejected: keeping pip+tox+setuptools (supersedes the repo-local decision recorded in
  `CLAUDE.md` / `openspec/config.yaml`).
- **DEC-2**: **Drop tox.** The Makefile is the dev interface; the CI matrix covers interpreters. —
  One tool fewer; rejected: tox driving Poetry envs locally.
- **DEC-3**: Support **Python 3.12, 3.13, 3.14**; `requires-python = ">=3.12"`. — 3.12 is the
  requested floor, 3.14 is current; rejected: 3.12-only, 3.12–3.13.
- **DEC-4**: **Latest stable majors** of every dependency (numpy 2, latest pandas, pytest, pytest-bdd,
  rdflib, pydantic, …); fix the breakage. — A "serious" upgrade; rejected: staying within current
  majors.
- **DEC-5**: **Prune** stale or misplaced dependencies: `toml` → stdlib `tomllib`; drop
  `py-singleton`; move `beautifulsoup4` to the test group; drop `tabulate` and `pytest-subtests`.
  — Fewer runtime deps for library consumers; rejected: bump-only.
- **DEC-6**: Release as **2.0.0**; public-API breaks are **allowed but bounded**: a break is
  permitted only where an upgrade or prune forces it, and every break is listed in `CHANGELOG.md`
  with its migration. — Dropping 3.11 already breaks consumers; rejected: 1.1.0 with a frozen API.
- **DEC-7**: Gates are **Ruff** (lint + format, replaces the unused flake8 config), **mypy**
  (non-strict baseline), **import-linter**, **`openspec validate --strict`**,
  aggregated by `make check-all` and run on every PR. — The library-archetype gate profile;
  rejected: gates only at release time (today's state for import-linter).
- **DEC-8**: **Gates land before the upgrade** (stage 2 before stage 3). — Breakage from new majors
  is then caught by lint/types/coverage, not by users; rejected: upgrade first.
- **DEC-10** (re-shape, 2026-10-30, owner decision): the **coverage floor (≥80%) is deferred to a
  follow-up change**. Coverage is still measured and reported; no `fail_under` here. — Keeps this
  change about tooling and upgrade; rejected: writing new tests inside this change.
- **DEC-9**: `AGENTS.md` canonical + thin `CLAUDE.md` pointer, both regular files (project-setup
  D8). — Fixes the detected symlink; rejected: keeping the symlink.

## Rabbit-holes

- **mypy on legacy code** may report many errors. Baseline is non-strict with
  `ignore_missing_imports`; residual errors are fixed or carried as explicit per-module overrides
  listed in `mypy.ini` — never a blanket `ignore_errors` on the whole package.
- **pytest-bdd major bump** changes feature-path resolution and Gherkin parsing; existing
  `tests/steps` may need path and step-signature updates. Keep feature files unchanged in meaning.
- **Live-network tests** (`test_describe_uri`, remote SPARQL) drift; they stay outside the gate.
- **TOML reading is untested and likely broken** (`toml.loads(bytes)`); the `tomllib` swap fixes it
  and gets a test.
- **Import-linter tightening** stops at contracts the current code already satisfies plus fixes
  that are a few lines; a structural refactor to satisfy a contract is out of scope (record it).

## No-gos

- No new features and no API redesign beyond what DEC-6 allows.
- No `infra/`, Dockerfile, deploy pipeline, or `sonar` config (library archetype).
- No re-layering (`models` stays the innermost layer; no `domain/`/`commons/` packages).
- No new Antora page stubs; docs change only where they describe build, install or supported
  Pythons.
- No coverage floor (DEC-10, follow-up change). No mypy `--strict`, no pre-commit hooks requirement, no release-please migration in this change.
- No change to `publish.yml`'s Trusted Publishing flow beyond what Poetry and the new Python matrix
  require.

---

## What Changes

- Pinned `openspec/schemas/meaningfy/` refreshed to skillery 3.7.0.
- `AGENTS.md` becomes a regular, canonical file; `CLAUDE.md` becomes a pointer that imports it.
- `.claude/memory/MEMORY.md` and `openspec/config.yaml` `context:` updated to the new tooling.
- **BREAKING** `requires-python` raised from `>=3.11` to `>=3.12`.
- **BREAKING** Build backend and dev workflow move from setuptools + pip + tox to Poetry; `tox.ini`
  deleted.
- Dedicated root configs: `ruff.toml`, `mypy.ini`, `pytest.ini`, `.coveragerc`.
- `make lint`, `make typecheck`, `make check-spec`, `make check-all`; PR CI runs `make check-all` on
  3.12/3.13/3.14.
- `.importlinter` contracts re-derived and tightened.
- All runtime and dev dependencies at latest stable majors; `toml`, `py-singleton`, `tabulate`,
  `pytest-subtests` removed; `beautifulsoup4` moved to the test group.
- `SECURITY.md` added; `CHANGELOG.md` 2.0.0 entry; `eds4jinja2/VERSION` → `2.0.0`.

## Capabilities

### New Capabilities
- `library-packaging`: how the library is built, which Pythons it supports, and what its installed
  wheel must provide.
- `quality-gates`: the single `make check-all` gate, its components, and its enforcement in CI.

### Modified Capabilities
- (none) — runtime behaviour of the data sources and report builder is unchanged; existing specs are
  proven by the existing test suite.

## Impact

- Code: `eds4jinja2/adapters/file_ds.py` (tomllib), `eds4jinja2/adapters/remote_sparql_ds.py`
  (singleton), plus whatever the new majors and Ruff/mypy surface.
- Build: `pyproject.toml`, `poetry.lock`, `Makefile`, `tox.ini` (deleted), new root configs.
- CI: `.github/workflows/main.yml`, `publish.yml`.
- Consumers: Python 3.11 users must stay on 1.x; 2.0.0 lists any API break in `CHANGELOG.md`.
- Repo docs: `AGENTS.md`, `CLAUDE.md`, `README.md` (install), `.claude/memory/MEMORY.md`,
  `openspec/config.yaml`.
