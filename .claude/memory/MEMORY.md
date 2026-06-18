<!-- Regenerable orientation INDEX for eds4jinja2. Auto-loaded each session (first ~200 lines) —
     keep ≤200 lines. INDEX, NOT authority: the truth is openspec/specs/ and openspec/config.yaml's
     `context:`. Stable, CONFIRMED facts only. -->

# Project Memory (index) — eds4jinja2

## Project Overview

- Library: embeds data-source specs (RDF/SPARQL + tabular files) into Jinja2 templates for
  dynamic report generation. PyPI package; CLI entrypoint `mkreport`.
- Top-level package: `eds4jinja2/` (no `/src`). Default branch: `master`.
- Real layers: `entrypoints → builders → adapters` (adapters innermost).
- Tooling: pip + tox + setup.py (NOT Poetry). Deps in requirements*.txt. Tests via tox
  (`py311`, `py312`). `make` is the dev/CI interface (`make install-all`, `make test-all`).
- Target interpreters: Python 3.11 and 3.12.

## Spine (where work and truth live)

- EPIC ≡ `openspec/changes/<id>/proposal.md`; PLAN ≡ `design.md` + `tasks.md`.
- Durable truth: `openspec/specs/`. Orientation: `openspec/config.yaml: context:`.
- Drive with `/opsx:*` after `npx @fission-ai/openspec init`.

## Key Decisions

- 2026-06-18: Added Python 3.12 support on top of master's tox/setup.py approach (kept tox; did
  NOT migrate to Poetry). Dropped Python 3.8 — numpy>=1.26 / pandas>=2.1 (needed for 3.12) require
  Python >=3.9. Bumped numpy ~=1.26.0, pandas ~=2.2.0.
- 2026-06-18: 3.12 code fix — distutils.copy_tree → shutil.copytree(dirs_exist_ok=True);
  `import collections` → `import collections.abc`. (master already fixed collections.Mapping and
  the pandas df.replace usage.)

## Gotchas

- numpy/pandas pinned for 3.12 cannot run on Python 3.8 — the two interpreters cannot share one
  requirements set. That is why 3.8 was dropped rather than kept.
- `tests/unit/test_sparql_ds.py::test_describe_uri` asserts on live remote DESCRIBE data from
  publications.europa.eu that has drifted; it can fail offline or when the remote data changes.
