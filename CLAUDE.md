<!-- meaningfy-template-version: 3.0.0 -->
<!-- CANONICAL agent instruction file (Claude Code loads CLAUDE.md). AGENTS.md is a SYMLINK to
     this file. Edit THIS file only — never AGENTS.md (CLAUDE-canonical; DEC-4). This file ROUTES
     to skills and to the global ~/.claude/CLAUDE.md standard; it never restates that standard. -->

# Project: eds4jinja2

Meaningfy project. A library that embeds data-source specifications (RDF/SPARQL endpoints and
tabular files) directly into Jinja2 templates to drive dynamic report generation. PyPI package
with a `mkreport` CLI. The company-wide standard lives in the **global `~/.claude/CLAUDE.md`** —
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

- **Real layers** (verified): `entrypoints → builders → adapters`. `adapters` is the innermost
  layer (imports nothing upward); `builders` orchestrates adapters; `entrypoints` (CLI `mkreport`)
  drives builders. This library keeps these real layer names.
- **Tooling is pip + tox + setup.py** (NOT Poetry): dependencies in `requirements.txt` /
  `requirements-dev.txt`, build via `setup.py`, tests via `tox` (envs `py311`, `py312`). The
  `make` targets are the dev/CI interface: `make install-all`, `make test-unit`,
  `make test-features`, `make test-all`.
- Target interpreters: **Python 3.11 and 3.12** (3.8 dropped — incompatible with the numpy/pandas
  versions needed for 3.12).
- The package version is the single source of truth in `eds4jinja2/__init__.py:__version__`
  (`setup.py` and `docs/conf.py` read it via regex).
- Tests: `tests/unit/` (unit) and `tests/steps/` + `tests/features/` (BDD). Some SPARQL tests hit
  live remote endpoints and need network; `test_describe_uri` asserts on remote data that can
  drift.
- Default branch is **`master`** (the PR target). Branch off it; never commit to it directly.

## `.claude/` is a regenerable index — the truth is `openspec/specs/`

`.claude/memory/MEMORY.md` is a cheap orientation note (≤200 lines; stable patterns only). It is
an **index, not authority** — if it disagrees with `openspec/specs/`, `specs/` wins.

## Project specifics

- **Archetype:** library (pip-installable; published to PyPI; CLI entrypoint `mkreport`).
- **Top-level package:** `eds4jinja2/` (no `/src`).
- **Layers / modules:** `adapters` (data sources: file, local/remote SPARQL, namespaces, tabular),
  `builders` (Jinja env + report builder + actions), `entrypoints` (CLI).
- **Datastores / external systems:** SPARQL endpoints (remote + local rdflib), Fuseki for tests
  (`make start-fuseki`), tabular files (csv/tsv/xls/xlsx via pandas).
- **Deployable?** No — it is a library.

See `docs/` (Sphinx) for the existing methodology and API documentation.
