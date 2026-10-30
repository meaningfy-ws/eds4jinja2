## ADDED Requirements

### Requirement: One aggregate gate
`make check-all` SHALL run, and fail on the first failure of: Ruff lint and format check, mypy,
import-linter, `openspec validate --strict`, and the non-network test suite with coverage. Each
component SHALL also be runnable alone (`make lint`, `make typecheck`, `make check-architecture`,
`make check-spec`, `make test`).

#### Scenario: A lint violation fails the gate
- **WHEN** a module contains a Ruff violation and `make check-all` runs
- **THEN** the command exits non-zero and names the violating file

#### Scenario: Clean tree passes
- **WHEN** `make check-all` runs on the merged change
- **THEN** it exits 0

### Requirement: Coverage floor
The non-network test run SHALL fail when line coverage of the `eds4jinja2` package is below 80%.
Tests marked `network` SHALL NOT count toward the floor.

#### Scenario: Coverage below the floor
- **WHEN** coverage of the non-network run is 79%
- **THEN** `make test` exits non-zero and reports the shortfall

### Requirement: Tool configuration in dedicated root files
Lint, type, test and coverage configuration SHALL live in `ruff.toml`, `mypy.ini`, `pytest.ini` and
`.coveragerc` at the repository root; `pyproject.toml` SHALL NOT carry `[tool.ruff]`, `[tool.mypy]`,
`[tool.pytest]` or `[tool.coverage]` tables.

#### Scenario: Locating the pytest configuration
- **WHEN** a contributor looks for the pytest markers and options
- **THEN** they are in `pytest.ini`, and no other file defines pytest options

### Requirement: Layer contracts enforced on every pull request
The import-linter contracts SHALL be checked on every pull request, not only at release. In
addition to the existing upward-import bans, they SHALL forbid:
- `eds4jinja2.models` from importing the I/O and framework libraries `requests`, `SPARQLWrapper`,
  `rdflib`, `yaml`, `jinja2` and `click`;
- `eds4jinja2.services` from importing `click`, `requests` and `SPARQLWrapper` (remote I/O goes
  through adapters; the CLI framework stays in entrypoints).

#### Scenario: A model importing an adapter
- **WHEN** a module under `eds4jinja2/models` imports from `eds4jinja2.adapters` and a PR is opened
- **THEN** the PR's CI run fails on `make check-architecture`

#### Scenario: A model doing HTTP
- **WHEN** a module under `eds4jinja2/models` imports `requests`
- **THEN** `make check-architecture` fails naming the forbidden import

### Requirement: Canonical agent file
`AGENTS.md` SHALL be a regular file holding the repository's agent instructions, and `CLAUDE.md`
SHALL be a regular file that imports it (`@AGENTS.md`); neither SHALL be a symlink.

#### Scenario: Checking the agent files
- **WHEN** `test -L AGENTS.md || test -L CLAUDE.md` runs at the repository root
- **THEN** it exits non-zero (neither is a symlink), and `CLAUDE.md` contains the line `@AGENTS.md`
