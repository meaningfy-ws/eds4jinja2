<!-- Regenerable orientation INDEX for eds4jinja2. Auto-loaded each session (first ~200 lines) —
     keep ≤200 lines. INDEX, NOT authority: the truth is openspec/specs/ and openspec/config.yaml's
     `context:`. Stable, CONFIRMED facts only. -->

# Project Memory (index) — eds4jinja2

## Project Overview

- Library: embeds data-source specs (RDF/SPARQL + tabular files) into Jinja2 templates for
  dynamic report generation. PyPI package; CLI entrypoint `mkreport`.
- Top-level package: `eds4jinja2/` (no `/src`). Default branch: `master`.
- Layers: `entrypoints → services → adapters → models` (models innermost, pure), enforced by
  `.importlinter` (also bans I/O/framework imports in `models` and remote I/O/CLI in `services`).
- Tooling: Poetry (committed `poetry.lock`, PEP 735 groups `test`/`lint`), no tox. `make check-all`
  is the gate CI runs on 3.12/3.13/3.14. Tool config in root files (`ruff.toml`, `mypy.ini`,
  `pytest.ini`, `.coveragerc`).
- Version: `eds4jinja2/VERSION` is the truth; `pyproject.toml` copy checked by `make check-version`.

## Spine (where work and truth live)

- EPIC ≡ `openspec/changes/<id>/proposal.md`; PLAN ≡ `design.md` + `tasks.md`.
- Durable truth: `openspec/specs/`. Orientation: `openspec/config.yaml: context:`.
- `make check-spec` runs `openspec validate --all --strict` (needs Node.js).

## Gotchas

- pytest is pinned to 9.1.1: pytest-bdd 9.0.0 breaks on pytest 9.2 (`_arg2fixturedefs`).
- pandas 3: string columns are the `str` dtype; select them with `select_dtypes([object, "str"])`.
  Excel files are read with the `calamine` engine (python-calamine; no xlrd/openpyxl).
- Tests marked `network` hit live SPARQL endpoints and are excluded from the gate (`make
  test-network`); `test_describe_uri` asserts on remote data that can drift.
- Coverage is reported, not gated; the ≥80% floor is a planned follow-up change.
