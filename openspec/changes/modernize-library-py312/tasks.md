> Derives from: the EPIC in `openspec/changes/modernize-library-py312/proposal.md`

## 1. Spine and agent files (PR 1)

- [x] 1.1 Refresh `openspec/schemas/meaningfy/` to skillery 3.7.0
- [x] 1.2 Replace the `AGENTS.md` symlink with the canonical file; reduce `CLAUDE.md` to the pointer (quality-gates: Canonical agent file)
- [ ] 1.3 Regenerate `.claude/memory/MEMORY.md` and update `openspec/config.yaml` `context:` to Poetry / 3.12–3.14 / gates
- [ ] 1.4 `openspec validate --all --strict` passes (fix spec-format issues only)

## 2. Poetry and gates (PR 2)

- [x] 2.1 Migrate to Poetry at current dependency versions; delete `tox.ini`; Makefile targets use `poetry run` (library-packaging: Poetry build with a committed lock file)
- [x] 2.2 Move pytest/coverage config to `pytest.ini` and `.coveragerc`; drop flake8 config
- [ ] 2.3 Add `ruff.toml` + `make lint`; fix lint debt in its own commit
- [ ] 2.4 Add `mypy.ini` + `make typecheck`; fix or override per design D-4
- [x] 2.5 ~~Coverage floor~~ — deferred to a follow-up change (DEC-10)
- [ ] 2.6 Tighten `.importlinter` with the external-package contracts (quality-gates: Layer contracts enforced on every pull request)
- [ ] 2.7 Add `make check-version`, `make check-spec` and `make check-all`; `main.yml` runs `make check-all` and `poetry check --lock` (quality-gates: One aggregate gate)
- [ ] 2.8 Add `SECURITY.md`

## 3. Python 3.12+ and latest dependencies (PR 3)

- [ ] 3.1 `requires-python = ">=3.12"`, classifiers 3.12–3.14, CI matrix 3.12/3.13/3.14 in `main.yml` and `publish.yml` (library-packaging: Supported Python versions)
- [ ] 3.2 Prune: `toml` → `tomllib` with tests TC-001…TC-003; remove `py-singleton` (D-3) with test TC-004; move `beautifulsoup4` to the test group; drop `tabulate`, `pytest-subtests` (library-packaging: TOML files are read with the standard library; Installed wheel provides the CLI and runtime only)
- [ ] 3.3 Bump numpy + pandas (+ xlrd, openpyxl) to latest majors; fix breakage
- [ ] 3.4 Bump rdflib, SPARQLWrapper, pyoxigraph; fix breakage
- [ ] 3.5 Bump pydantic, Jinja2, click, PyYAML, requests; fix breakage
- [ ] 3.6 Bump pytest, pytest-bdd, pytest-cov, import-linter, ruff, mypy; fix step definitions/paths
- [ ] 3.7 Ruff `UP` autofix pass for 3.12 syntax; `make check-all` green on 3.12, 3.13, 3.14

## 4. Release 2.0.0 (PR 3, final commits)

- [ ] 4.1 `eds4jinja2/VERSION` → `2.0.0`; `CHANGELOG.md` 2.0.0 with a Breaking section (3.11 dropped, Poetry, every API break + migration)
- [ ] 4.2 Smoke-test the wheel in a fresh venv: `mkreport --help` exits 0; `import bs4` fails (library-packaging: Installed wheel provides the CLI and runtime only)
- [ ] 4.3 Update `README.md` install/dev instructions and the docs pages that mention tox, pip extras or Python versions
- [ ] 4.4 Find downstream dependents of eds4jinja2; confirm each pins `<2` or is ready for 2.0.0 before publishing

## Roadmap

- [x] 1.1 · [ ] 1.2 · [ ] 1.3 · [ ] 1.4 · [ ] 2.1 · [ ] 2.2 · [ ] 2.3 · [ ] 2.4 · [ ] 2.5 · [ ] 2.6 · [ ] 2.7 · [ ] 2.8 · [ ] 3.1 · [ ] 3.2 · [ ] 3.3 · [ ] 3.4 · [ ] 3.5 · [ ] 3.6 · [ ] 3.7 · [ ] 4.1 · [ ] 4.2 · [ ] 4.3 · [ ] 4.4

## Verification

`make check-all` green on 3.12/3.13/3.14 in PR CI, `openspec validate modernize-library-py312 --strict` passes, PLAN scored ≥9/10 by `clarity-gate` before `/opsx:apply`.
