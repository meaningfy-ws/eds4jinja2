## ADDED Requirements

### Requirement: Documentation is authored in AsciiDoc and built by Antora

The project documentation SHALL be authored in AsciiDoc and built into a static HTML site by Antora,
and the Sphinx/reStructuredText toolchain SHALL be removed.

#### Scenario: AsciiDoc sources build with Antora
- **WHEN** the documentation build is run against `docs/antora-playbook.local.yml`
- **THEN** Antora produces a static HTML site under `docs/build/site` whose entry page is generated
  from `docs/modules/ROOT/pages/index.adoc`

#### Scenario: No Sphinx toolchain remains
- **WHEN** the repository is inspected after the migration
- **THEN** `docs/conf.py`, `docs/index.rst`, `docs/srcdocs/`, `docs/Makefile`, and `docs/make.bat`
  are absent, and the `pyproject.toml` `docs` extra (Sphinx, myst-parser, sphinxcontrib-apidoc) is
  removed

### Requirement: The site is navigable, enriched, and covers the public surface

The documentation SHALL be organised into multiple navigable pages covering getting started, the
data sources, in-memory graphs, parallel execution, templating, the CLI, a curated public-API
reference, extending the library, and the architecture; a navigation tree SHALL link them.

#### Scenario: Navigation lists every topic page
- **WHEN** the site is built
- **THEN** the navigation rendered from `docs/modules/ROOT/nav.adoc` links the getting-started,
  data-sources, in-memory-graphs, parallel-execution, templating, CLI, API-reference, extending, and
  architecture pages

#### Scenario: The public API is documented without dumping private members
- **WHEN** a reader opens the API-reference page
- **THEN** it documents the public surface (`build_eds_environment`, `ReportBuilder`, the
  data-source builders, and the `DataSource` `(content, error)` contract) as curated content, not an
  autodoc dump of private (`_`-prefixed) members

### Requirement: The documentation is buildable locally via make

The repository SHALL expose `make` targets that build and preview the documentation locally so a
developer has a local view of the site.

#### Scenario: A developer builds the site locally
- **WHEN** a developer runs `make build-docs`
- **THEN** the Antora site is generated under `docs/build/site` from the local working tree

#### Scenario: A developer previews the site locally
- **WHEN** a developer runs `make preview-docs`
- **THEN** the site is built and served over HTTP on a local port

### Requirement: GitHub Actions builds on pull requests and deploys to GitHub Pages on master

A GitHub Actions workflow SHALL build the documentation on pull requests targeting `master` and,
on push to `master`, deploy the built site to GitHub Pages.

#### Scenario: Pull request triggers a documentation build
- **WHEN** a pull request targeting `master` changes documentation sources
- **THEN** the workflow builds the Antora site and the build must succeed for the check to pass

#### Scenario: Push to master deploys to GitHub Pages
- **WHEN** a commit is pushed to `master`
- **THEN** the workflow builds the site and deploys it to GitHub Pages at the project Pages URL

### Requirement: ReadTheDocs builds the same AsciiDoc source

ReadTheDocs SHALL build the documentation from the same Antora playbook so the existing
`readthedocs.io` URL continues to work, without requiring Sphinx.

#### Scenario: ReadTheDocs builds via Antora
- **WHEN** ReadTheDocs runs the build defined in `.readthedocs.yml`
- **THEN** it installs Antora and builds the HTML site from `docs/antora-playbook.yml` into the
  ReadTheDocs HTML output directory, with no Sphinx step
