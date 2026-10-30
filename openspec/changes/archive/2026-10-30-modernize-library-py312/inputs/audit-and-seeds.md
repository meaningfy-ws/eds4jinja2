<!-- SECONDARY input — preserved, never groomed. The EPIC (proposal.md) supersedes it. -->

# Seeds, audit and Q&A — modernize-library-py312

## Human seed (2026-10-30)

> "Check how well this library aligns to the meaningfy project setup, audit the minimal necessary
> for this library, then we will make a serious upgrade to the latest library versions, python 3.12
> minimum. Start a new epic change if one does not exist for this purpose; also check if the
> openspec schema aligns to the latest meaningfy schema."

## Inputs read

- `project-setup` skill 3.7.0: `modernizing-existing-projects.md`, `spine-projection.md`,
  `decisions.md` (D8), `scaffold.sh --dry-run` gap report (archetype `library`).
- Repo: `pyproject.toml`, `tox.ini`, `Makefile`, `.importlinter`, `.github/workflows/*`,
  `openspec/` (config, schema, specs, archive), `AGENTS.md`/`CLAUDE.md`, `.claude/memory/MEMORY.md`.
- Dependency usage scan (`grep` of imports in `eds4jinja2/` and `tests/`).

## Audit — detected gaps only (library archetype)

| Dimension | Finding | Status |
|---|---|---|
| Spine schema | `openspec/schemas/meaningfy/` was a pre-3.7.0 snapshot (old appetite scale, `Parent:` line, no `spec.md`/`tasks.md` diff, error matrix lacks "detected by"). Refreshed to 3.7.0 at the start of this change. | ⚠️ → fixed in slice 1 |
| Agent file | `AGENTS.md` is a symlink → `CLAUDE.md` (violates D8). | ❌ |
| Memory index | `.claude/memory/MEMORY.md` is stale (says `builders`, Python 3.11, pip+tox). | ⚠️ |
| Packaging | pip + tox + setuptools; standard is Poetry. | ⚠️ (deviation, now dropped) |
| Tool configs | pytest / coverage / flake8 config lives in `tox.ini`; no `ruff.toml`, `mypy.ini`, `pytest.ini`, `.coveragerc`. | ❌ |
| Lint / types | flake8 configured but run nowhere; no Ruff, no mypy. | ❌ |
| Coverage | measured, uploaded to Codecov, but no `fail_under` gate. | ❌ |
| Architecture in CI | `make check-architecture` runs only in `publish.yml`, not on PRs (`main.yml`). | ⚠️ |
| Spine in CI | no `openspec validate --strict` target or CI step. | ❌ |
| Release governance | no `SECURITY.md`. `publish.yml` (Trusted Publishing) present. | ❌ |
| Versions | `requires-python >=3.11`; CI 3.11/3.12. | ⚠️ |

Not carried (not needed for a library, by judgement): `infra/`, Dockerfile, `domain/`/`commons/`
packages (`models` is this repo's innermost layer), extra Antora page stubs, `sonar-project.properties`,
type-split test dirs (`tests/unit` + `tests/steps`/`tests/features` already split by type).

## Dependency usage scan

- `toml` — used once (`adapters/file_ds.py`), as `toml.loads(bytes)`, which is a latent bug (expects
  `str`); `.toml` reading is untested.
- `py-singleton` — one decorator on `SPARQLClientPool` (`adapters/remote_sparql_ds.py`).
- `beautifulsoup4` — runtime dependency but imported only by tests.
- `tabulate`, `pytest-subtests` — unused (one commented-out `tabulate` reference).
- `xlrd`, `openpyxl` — not imported; pandas `read_excel` backends (keep).

## Q&A record

| Question | Answer |
|---|---|
| Packaging: keep pip+tox or Poetry? | **Migrate to Poetry.** |
| Python versions? | **3.12–3.14** (`requires-python >=3.12`). |
| One epic or two? | **One epic, staged.** |
| Alignment scope? | **Ruff, coverage ≥80%, mypy, SECURITY.md + openspec validate**, and "derive and check if importlinter can be improved". |
| Keep tox? | **Drop tox.** |
| Major versions? | **Latest majors, fix breakage.** |
| Prune deps? | **Yes, prune.** |
| API break / version? | **Allow breaks → 2.0.0.** |

## Downstream dependents (task 4.4, `gh search code eds4jinja2 --owner meaningfy-ws`, 2026-10-30)

| Repo | Pin | Affected by 2.0.0? |
|---|---|---|
| lam-validator | `eds4jinja2==0.1.34` | No |
| lam-workflow | `eds4jinja2==0.2.0` | No |
| rdf-fingerprinter-ws | `eds4jinja2~=0.2.0` | No |
| rdf-differ-ws | `eds4jinja2>=0.3.1,<0.4` | No. Its openspec notes ask for relaxed rdflib/requests pins, which 2.0.0 provides. |
| **lam4doc** | `git+https://github.com/meaningfy-ws/eds4jinja2@master` | **Yes. It tracks `master`, so it gets 2.0.0 on merge.** It needs a pin (`@1.0.4` tag or `eds4jinja2<2`) before this merges. |
