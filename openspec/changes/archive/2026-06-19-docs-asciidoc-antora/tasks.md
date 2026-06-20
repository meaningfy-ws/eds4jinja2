<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [x]` checkboxes. -->

> Derived from EPIC `docs-asciidoc-antora` (proposal.md)  <!-- cite your parent (golden thread) -->

## 1. Antora scaffold

- [x] 1.1 Add `docs/antora.yml` (name `eds4jinja2`, title, `version: '~'`, nav)
- [x] 1.2 Add `docs/antora-playbook.yml` (production: GitHub source, `start_path: docs`, branch `master`, site url = Pages URL, stock UI bundle, lunr extension, asciidoc attributes)
- [x] 1.3 Add `docs/antora-playbook.local.yml` (local: `url: ./..`, `branches: [HEAD]`)
- [x] 1.4 Add `package.json` pinning `antora@^3.1` + `@antora/lunr-extension` (devDependencies)
- [x] 1.5 Add `docs/modules/ROOT/nav.adoc` listing all pages in reading order

## 2. Content migration + enrichment (AsciiDoc pages)

- [x] 2.1 `pages/index.adoc` — what it is, why/problems solved, data-source matrix, "next steps" links
- [x] 2.2 `pages/getting-started.adoc` — install (+`[oxigraph]`), quick start A (env) & B (`mkreport`), report-folder convention
- [x] 2.3 `pages/data-sources.adoc` — every builder, `fetch_tabular` vs `fetch_tree`, the `(content, error)` fail-safe contract
- [x] 2.4 `pages/in-memory-graphs.adoc` — `from_graph`/`from_rdf` + the `ReportBuilder` injection pattern (override `from_endpoint`)
- [x] 2.5 `pages/parallel-execution.adoc` — `parallelism` config, all-or-nothing, threading caveats
- [x] 2.6 `pages/templating.adoc` — `config.json` shape, `conf` vars, HTML vs LaTeX flavour + delimiters
- [x] 2.7 `pages/cli.adoc` — `mkreport` args + target directory layout
- [x] 2.8 `pages/api-reference.adoc` — curated public API (`build_eds_environment`, `ReportBuilder`, `DataSource` contract, `InMemorySPARQLDataSource`, graph store)
- [x] 2.9 `pages/extending.adoc` — add a data source / engine; builder injection; respect the layers
- [x] 2.10 `pages/architecture.adoc` — Cosmic layers (ASCII diagram), tooling/`make`, version SSOT

## 3. Build & publish wiring

- [x] 3.1 Add `make` targets: `install-antora`, `build-docs`, `clean-docs`, `serve-docs`, `preview-docs` (+ Node vars, `.PHONY`)
- [x] 3.2 Add `.github/workflows/docs.yml`: build on PR; deploy to GitHub Pages on push to `master`
- [x] 3.3 Convert `.readthedocs.yml` to the Antora `build.jobs` form (Node 22, HTML only)

## 4. Remove the Sphinx stack

- [x] 4.1 Delete `docs/conf.py`, `docs/index.rst`, `docs/srcdocs/`, `docs/Makefile`, `docs/make.bat`
- [x] 4.2 `pyproject.toml`: remove the `docs` extra; change `dev` to drop `,docs`
- [x] 4.3 `.gitignore`: add `docs/build/` and `node_modules/`
- [x] 4.4 `README.md`: point "Documentation" at the Pages site (RTD as mirror), keep/fix badges

## 5. Verify locally

- [x] 5.1 `make build-docs` is green: `docs/build/site/index.html` exists, all nav pages render, no missing-xref errors
- [x] 5.2 No Sphinx residue: `grep -ri sphinx docs/ pyproject.toml .readthedocs.yml` is empty
- [x] 5.3 Package untouched: `make check-architecture` and `make test-all` still pass

## 6. Ship

- [x] 6.1 Branch, commit (Conventional Commits), push, open PR against `master`
- [x] 6.2 PR CI green (docs build job + existing test jobs) → merge
- [x] 6.3 Verify deployment: `deploy` job succeeds and the Pages URL serves the new site (HTTP 200, title + nav present)
- [x] 6.4 Bump patch version + CHANGELOG entry; cut the GitHub Release; confirm publish workflow green
