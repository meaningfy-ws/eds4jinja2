<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: the EPIC in `openspec/changes/modernize-library-py312/proposal.md`

## Context

eds4jinja2 1.0.4 is a PEP 621 setuptools package driven by pip + tox, tested on 3.11/3.12. The
audit (`inputs/audit-and-seeds.md`) lists the detected gaps. Layers: `entrypoints → services →
adapters → models`, with three import-linter contracts that today run only in `publish.yml`.
Downstream programs install released versions from PyPI; 1.x stays available after 2.0.0 ships.

## Goals / Non-Goals

**Goals:**
- `make check-all` = the whole gate, green on 3.12/3.13/3.14, run by PR CI (DEC-7).
- Poetry build with lock file; tox gone (DEC-1, DEC-2).
- Every dependency at latest stable major; stale ones pruned (DEC-4, DEC-5).
- `library-packaging` and `quality-gates` spec deltas satisfied.

**Non-Goals:** everything under the EPIC's No-gos.

## Decisions

- **D-1 Poetry layout = the Meaningfy template.** Follow
  `project-setup/assets/templates/root/pyproject.toml.tmpl`: PEP 621 `[project]`, PEP 735
  `[dependency-groups]` named `test`, `lint`, `dev`; `[tool.poetry] packages = [{ include =
  "eds4jinja2" }]`; backend `poetry-core>=2.0.0,<3.0.0`. `oxigraph` stays a
  `[project.optional-dependencies]` extra. Version: `eds4jinja2/VERSION` stays the single source
  (runtime reads it); `[project].version` is a static copy, and `make check-version` (part of
  `check-all`) fails when `poetry version -s` ≠ `cat eds4jinja2/VERSION` — the template's own
  "keep in sync" rule, made mechanical.
- **D-2 Runtime ranges, not `==` pins (deviation from the template).** Runtime deps are
  `>=X.Y,<X+1` on the resolved major; `test`/`lint`/`dev` groups use `==` as the template does.
  *Why:* the template targets applications; a library pinned `==` forces its versions onto every
  consumer's resolver. Rejected: template `==` pins for runtime.
- **D-7 "Latest" is resolved, not guessed.** For each family in tasks 3.3–3.6 run
  `poetry show --outdated --top-level`, take the newest non-pre-release version that has wheels for
  3.12, 3.13 and 3.14, and record the before → after versions in the CHANGELOG 2.0.0 entry.
- **D-8 Size of an in-scope fix.** A fix for a tightened import-linter contract or a mypy error is
  in scope when it touches ≤20 lines and moves no module between packages; anything larger is
  dropped from the contract / overridden in `mypy.ini` and recorded under Open Questions.
- **D-9 Coverage measurement.** `poetry run pytest -m "not network" --cov=eds4jinja2
  --cov-report=term` with `.coveragerc` `[report] fail_under = 80`, `omit = */__init__.py`; the
  baseline number is recorded in the task 2.5 commit message.
- **D-3 Singleton removal.** `SPARQLClientPool` holds all state in a class-level
  `threading.local()` behind static methods, so `@singleton` adds nothing. Delete the decorator,
  the `from py_singleton import singleton` import and the module-level `SPARQLClientPool.instance()`
  call (`adapters/remote_sparql_ds.py:58`). The only caller,
  `SPARQLClientPool.create_or_reuse_connection(...)` (line 87), is unchanged. *Why:* dead
  dependency; rejected: a replacement singleton mechanism (nothing needs one).
- **D-4 mypy baseline.** `mypy.ini`: `python_version = 3.12`, `ignore_missing_imports = True`,
  `check_untyped_defs = False`. Per-module `[mypy-eds4jinja2.x]` overrides only where a fix is out of
  scope, each with a one-line reason comment.
- **D-5 Ruff rules.** `select = ["E", "F", "W", "I", "UP", "B"]`, `line-length = 127` (current
  flake8 value), `target-version = "py312"`. `UP` does the 3.12 syntax modernisation automatically.
- **D-6 Gate ordering in `check-all`.** `check-version → lint → typecheck → check-architecture → check-spec → test`
  (cheap first). `check-spec` runs `npx -y @fission-ai/openspec@1.4.1 validate --all --strict`; CI
  sets up Node for it (already done in `docs.yml`).

## Algorithm / approach

Staged, one PR per stage, each green on `make check-all` (or, before 2.x exists, on the old test
command) before the next starts:

1. **Spine & agents** — schema copy (already applied on the branch), `git rm AGENTS.md` symlink →
   `git mv`-style content move: `CLAUDE.md` content becomes `AGENTS.md`; new `CLAUDE.md`:
   ```markdown
   # CLAUDE.md
   Read `AGENTS.md` — it is the canonical agent file for this repo.
   @AGENTS.md
   ```
   Regenerate `MEMORY.md` from code + `openspec/specs/`; update `config.yaml` `context:`.
2. **Gates** — Poetry migration first (keeps current versions, only the tool changes, so failures
   are attributable), then root configs, then each gate added one at a time with its debt fixed
   in its own commit. Coverage: measure; if <80%, add `models` unit tests until ≥80%.
3. **Upgrade** — `requires-python` → `>=3.12`; bump runtime deps one family at a time
   (numpy+pandas, rdflib+SPARQLWrapper, pydantic, Jinja2+click, rest), then test deps
   (pytest, pytest-bdd, pytest-cov), running `make check-all` after each; prune per DEC-5.
   Worked example of the TOML fix:
   ```python
   elif self._file_extension in [".toml"]:
       return tomllib.loads(self.file_path.read_text(encoding="utf-8"))
   ```

Idempotency: all steps are file edits and `poetry lock`, safe to re-run; the only non-repeatable
act is the PyPI release, which `publish.yml` already guards (a version can be uploaded once).

### Anti-patterns
| Don't | Do instead | Why |
|---|---|---|
| Bump all deps in one commit | One dependency family per commit | Breakage is attributable and revertible |
| `# type: ignore` / `noqa` sprinkled to go green | Fix, or a per-module override with a reason | Silenced gates erode silently |
| Lower `fail_under` to pass | Add tests for uncovered `models` code | The floor is the point |
| Edit `.feature` meaning to satisfy pytest-bdd 8 | Fix step definitions and paths | Features are the behaviour contract |
| Change public signatures "while we're here" | Only breaks forced by DEC-6, logged in CHANGELOG | Bounded 2.0.0 break |

## Test cases

Acceptance scenarios live in the spec deltas
([library-packaging](specs/library-packaging/spec.md),
[quality-gates](specs/quality-gates/spec.md)); this table is the test inventory that proves them.
The existing unit + BDD suite (non-network) is the regression proof that runtime behaviour is unchanged.

| ID | Layer / kind | Input | Expected | Edge cases |
|---|---|---|---|---|
| TC-001 | adapters, unit | `FileDataSource("x.toml")` with `a = 1\n[b]\nc = "d"` | tree `{"a": 1, "b": {"c": "d"}}` | — |
| TC-002 | adapters, unit | empty `.toml` file | tree `{}` | zero bytes |
| TC-003 | adapters, unit | invalid TOML (`a = `) | `fetch_tree()` returns `(None, <error message>)` via the existing `DataSource` fail-safe, no exception escapes | UTF-8 non-ASCII value parses |
| TC-004 | adapters, unit | `create_or_reuse_connection(url)` twice in one thread, without `py-singleton` installed | the same `SPARQLWrapper` both times | a second thread gets a different wrapper for the same `url` |
| TC-005 | build, unit (make) | `VERSION`=`2.0.0`, `[project].version`=`1.0.4` | `make check-version` exits non-zero | equal values → exit 0 |
| TC-006 | architecture | temp module in `models` importing `requests` | `make check-architecture` fails naming it | services importing `click` also fails |
| IT-001 | packaging | `make build`; fresh venv; `pip install dist/*.whl` | `mkreport --help` exits 0; `import bs4` raises `ImportError` | install with `[oxigraph]` extra pulls `pyoxigraph` |
| IT-002 | packaging | `pip install dist/*.whl` on Python 3.11 | pip refuses (`requires-python`) | — |
| IT-003 | CI | PR with a Ruff violation | `main.yml` fails on all three matrix legs at `make lint` | clean PR → green on 3.12/3.13/3.14 |

TC-001…TC-004 are pytest tests under `tests/unit/adapters/`; TC-005/TC-006 and IT-001/IT-002 are
manual verification steps recorded in the PR description; IT-003 is observed on PR 2.

## Error matrix

| Failure mode | How it is detected | Expected handling |
|---|---|---|
| A dep has no wheel for 3.14 | `poetry install` fails on the 3.14 CI leg | Use the latest version with 3.14 wheels; if none, record in Open Questions and ask before dropping 3.14 |
| New major breaks behaviour | Unit/BDD tests fail after that family's bump | Fix code; if the fix changes a public API, log it under 2.0.0 Breaking in `CHANGELOG.md` |
| Network test drifts | Only in `make test-network` | Not a gate failure; leave as is |
| Coverage <80% after upgrade | `make test` fails with the shortfall | Add tests; do not lower the floor |
| import-linter tightened contract fails | `make check-architecture` | Fix if within D-8; otherwise drop that clause and record it under Open Questions |
| mypy error outside D-8 | `make typecheck` | Per-module override in `mypy.ini` with a one-line reason |
| `openspec validate --strict` fails on archived/legacy specs | `make check-spec` | Fix the spec format (headings/scenarios); no semantic changes |
| Downstream consumer unpinned | Pre-release check of known dependents | Ask owners to pin `eds4jinja2<2` before publishing 2.0.0 |

## Risks / Trade-offs

- [pandas latest major changes dtype/str defaults] → covered by `test_tabular_utils` and BDD file
  scenarios; fix at the bump commit.
- [Poetry migration changes the published metadata] → compare `twine check` + wheel `METADATA`
  before/after for name, entry point, extras.
- [mypy noise slows stage 2] → non-strict baseline (D-4).
- [Unpinned downstream users get 2.0.0] → semver major + CHANGELOG + pin check (task 4.4).

## References

| Topic | Location |
|---|---|
| Audit and Q&A | [inputs/audit-and-seeds.md](inputs/audit-and-seeds.md) |
| Decisions DEC-1…DEC-9 | [proposal.md#key-decisions](proposal.md#key-decisions) |
| Agent-file rule (D8) | `project-setup` skill, `references/decisions.md` § "D8 — AGENTS.md canonical, CLAUDE.md a pointer, never a symlink" |
| Brownfield slice order | `project-setup` skill, `references/modernizing-existing-projects.md` § "2. Plan — order the gaps safely" |
| pyproject template | `project-setup` skill, `assets/templates/root/pyproject.toml.tmpl` |
| Current layer contracts | [/.importlinter](../../../.importlinter) |
| Layer spec | [openspec/specs/cosmic-layer-restructure/spec.md](../../specs/cosmic-layer-restructure/spec.md) |

## Open Questions

- None blocking. Which internal Meaningfy projects depend on eds4jinja2 is resolved at task 4.4
  (GitHub dependents search), not guessed here.
