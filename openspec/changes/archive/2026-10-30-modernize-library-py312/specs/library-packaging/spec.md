## ADDED Requirements

### Requirement: Supported Python versions
The library SHALL declare `requires-python = ">=3.12"` and SHALL be tested on CPython 3.12, 3.13
and 3.14.

#### Scenario: Installing on an unsupported interpreter
- **WHEN** a user runs `pip install eds4jinja2==2.*` on Python 3.11
- **THEN** pip refuses the install because the interpreter does not satisfy `requires-python`

#### Scenario: Test matrix covers every supported interpreter
- **WHEN** a pull request targets `master`
- **THEN** CI runs the gate on Python 3.12, 3.13 and 3.14, and the PR is blocked if any leg fails

### Requirement: Poetry build with a committed lock file
The project SHALL be built with Poetry from `pyproject.toml`, SHALL commit `poetry.lock`, and SHALL
NOT contain `setup.py`, `requirements*.txt` or `tox.ini`. The version SHALL be read from
`eds4jinja2/VERSION`.

#### Scenario: Building the distribution
- **WHEN** `make build` runs on a clean checkout
- **THEN** an sdist and a wheel are produced whose version equals the content of `eds4jinja2/VERSION`

#### Scenario: Lock file in sync
- **WHEN** `poetry check --lock` runs in CI
- **THEN** it passes, proving `poetry.lock` matches `pyproject.toml`

### Requirement: Installed wheel provides the CLI and runtime only
The installed wheel SHALL expose the `mkreport` console script and SHALL NOT pull test-only
dependencies (`beautifulsoup4`, pytest and its plugins) into a runtime install.

#### Scenario: CLI available after install
- **WHEN** the built wheel is installed into a fresh virtualenv and `mkreport --help` is run
- **THEN** the command exits 0 and prints its usage

#### Scenario: Runtime install excludes test dependencies
- **WHEN** the built wheel is installed into a fresh virtualenv without extras
- **THEN** `import bs4` fails in that environment

### Requirement: TOML files are read with the standard library
`FileDataSource` SHALL parse `.toml` files with the standard-library `tomllib` and SHALL return the
parsed mapping as its tree representation.

#### Scenario: Fetch a TOML file as a tree
- **WHEN** a `FileDataSource` points at a valid `.toml` file and its tree is fetched
- **THEN** the result is the dictionary that `tomllib` parses from that file
