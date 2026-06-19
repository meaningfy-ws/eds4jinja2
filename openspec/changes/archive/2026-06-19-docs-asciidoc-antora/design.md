<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Parent: EPIC `docs-asciidoc-antora` (proposal.md) — derived from DEC-1..DEC-6.

## Context

Today's docs are Sphinx + reStructuredText:

- `docs/conf.py` — Sphinx config; `extensions = [sphinxcontrib.apidoc, autodoc, intersphinx,
  viewcode]`; `autodoc_default_options` includes `private-members` (dumps `_` members).
- `docs/index.rst` — one 385-line page (install, why, data sources, LaTeX, CLI, `ReportBuilder`,
  extending, architecture) + an autodoc `srcdocs/modules` toctree.
- `docs/srcdocs/*.rst` — autodoc stubs. `docs/Makefile`, `docs/make.bat` — Sphinx make wrappers.
- `.readthedocs.yml` — builds Sphinx, installs the package `[docs]` extra, emits HTML/PDF/EPUB.
- `pyproject.toml` — `docs = ["myst-parser~=2.0.0", "Sphinx~=7.1.2", "sphinxcontrib-apidoc~=0.4.0"]`,
  referenced by `dev = ["eds4jinja2[test,docs]", ...]`.

The house pattern (verified by reading the files) is **Antora 3.1 + AsciiDoc**:

- `mapping-suite-sdk` (a published Python lib, like us): `docs/antora.yml`, `docs/antora-playbook.yml`
  (production, source = the GitHub repo `docs/` on the default branch), `docs/antora-playbook.local.yml`
  (source = `./..` `branches: [HEAD]`), stock `antora-ui-default` UI bundle, `.readthedocs.yaml` using
  `build.jobs` (Node 22, `antora --fetch ... --to-dir $READTHEDOCS_OUTPUT/html`), and Makefile targets
  `build-docs` / `clean-docs` / `install-antora` / `run-antora` driving `npx antora`.
- `entity-resolution-docs`: same scaffold + a committed `package.json`, the `@antora/lunr-extension`
  search, and a `.github/workflows/docs-build-deploy.yaml` that runs `make build-docs` then
  `upload-pages-artifact` → `deploy-pages` to **GitHub Pages**.

We combine both: the `mapping-suite-sdk` RTD path **and** the `entity-resolution-docs` Pages path,
from one playbook.

## Goals / non-goals

- **Goal**: a navigable, searchable, enriched AsciiDoc site; one-command local build/preview; PR
  build validation; auto-deploy to GitHub Pages on `master`; RTD kept working; Sphinx fully removed.
- **Non-goal**: any change to `eds4jinja2/` code, the public API, the methodology, a custom theme,
  Mermaid, PDF/EPUB, multi-version docs, or docstring autodoc (see No-gos).

## Target layout

```
docs/
  antora.yml                      # component: name eds4jinja2, version '~', nav
  antora-playbook.yml             # production: source = github repo, start_path docs, branch master
  antora-playbook.local.yml       # local: source = ./.. , branches [HEAD]
  package.json                    # antora ^3.1 + @antora/lunr-extension (dev)
  modules/ROOT/
    nav.adoc
    pages/
      index.adoc                  # what & why, problems solved, data-source matrix, next steps
      getting-started.adoc        # install (+oxigraph extra), quick start A (env) & B (mkreport), report folder
      data-sources.adoc           # every builder; fetch_tabular vs fetch_tree; (content,error) contract
      in-memory-graphs.adoc       # from_graph / from_rdf; the ReportBuilder injection pattern
      parallel-execution.adoc     # parallelism config, all-or-nothing, threading caveats
      templating.adoc             # config.json shape, conf vars, HTML vs LaTeX flavour + delimiters
      cli.adoc                    # mkreport args + target directory layout
      api-reference.adoc          # curated: build_eds_environment, ReportBuilder, DataSource, InMemorySPARQLDataSource, graph store
      extending.adoc              # add a data source / engine; builder injection; respect the layers
      architecture.adoc           # Cosmic layers (ASCII diagram), tooling/make, version SSOT
```

Config files mirror the siblings nearly verbatim (only names/URLs change):

- `antora.yml`: `name: eds4jinja2`, `title: eds4jinja2`, `version: '~'`, `nav: [modules/ROOT/nav.adoc]`.
- `antora-playbook.yml`: `site.url: https://meaningfy-ws.github.io/eds4jinja2`,
  `start_page: eds4jinja2::index.adoc`; content source
  `https://github.com/meaningfy-ws/eds4jinja2.git`, `start_path: docs`, `branches: [master]`;
  stock UI bundle; lunr extension under `antora.extensions`; standard asciidoc attributes.
- `antora-playbook.local.yml`: same, but content source `url: ./..`, `branches: [HEAD]` for local
  preview of the working tree.

## Build & publish wiring

- **Make** (Node-based, modelled on the siblings but trimmed):
  - vars: `NODE/NPM/NPX := $(shell command -v ...)`, `DOC_BUILD_DIR=docs/build`,
    `ANTORA_PLAYBOOK=$(PWD)/docs/antora-playbook.local.yml`.
  - `install-antora` (guard Node present, `npm install` from committed `package.json`),
    `build-docs` (`npx antora $(ANTORA_PLAYBOOK)`), `clean-docs` (`rm -rf docs/build`),
    `serve-docs` (`python3 -m http.server 8088 --directory docs/build/site`),
    `preview-docs: build-docs serve-docs`. Add all to `.PHONY`.
- **GitHub Actions** `.github/workflows/docs.yml` (modelled on `entity-resolution-docs`, branch
  `master`):
  - `on: push: branches:[master]` + `pull_request: branches:[master]` (paths: `docs/**`,
    `package.json`, the workflow, `README.md`).
  - `build` job: checkout (fetch-depth 0), setup-node 22, `make build-docs`, on push to master
    `actions/upload-pages-artifact@v3` with `path: docs/build/site`.
  - `deploy` job: `if push to master`, `needs: build`, `permissions: pages: write, id-token: write`,
    `environment: github-pages`, `actions/deploy-pages@v4`.
  - Node major aligns with the repo's existing "Node 24-era actions" stance: use the current major
    tags (`actions/checkout@v4`/v6 as available, `actions/setup-node@v4`, the Pages actions at their
    current majors) consistent with `main.yml`/`publish.yml`.
- **ReadTheDocs** `.readthedocs.yml` → exactly the `mapping-suite-sdk` `build.jobs` form, branch
  `master`, HTML only (drop `formats: [pdf, epub]`).

## Removals & edits

- Delete: `docs/conf.py`, `docs/index.rst`, `docs/srcdocs/`, `docs/Makefile`, `docs/make.bat`.
- `pyproject.toml`: remove the `docs` extra entirely; change `dev` to `eds4jinja2[test]` (drop
  `,docs`). No other dependency change.
- `.gitignore`: add `docs/build/` and `node_modules/` (keep the existing `docs/_build/` line; it is
  harmless legacy).
- `README.md`: "Documentation" section points to the Pages site as canonical and notes the RTD
  mirror; keep the RTD badge (it still resolves); fix the link text accordingly.
- `CHANGELOG.md`: new `[x.y.z]` entry under a docs/tooling heading; update the version-compare links.

## Content migration map (source → page)

| Current `index.rst` / `README.md` topic | New page |
|---|---|
| "But why?" / benefits / problems solved | `index.adoc` |
| install + `[oxigraph]` extra + quick start A/B + report folder convention | `getting-started.adoc` |
| supported data sources list + the README data-source table + `(content,error)` | `data-sources.adoc` |
| In-memory graph data sources + injection pattern | `in-memory-graphs.adoc` |
| Parallel report execution | `parallel-execution.adoc` |
| config.json shape + LaTeX templates + delimiters | `templating.adoc` |
| CLI usage + target directory layout | `cli.adoc` |
| `ReportBuilder` params + public API | `api-reference.adoc` (curated) |
| Extending eds4jinja2 (new source / engine / injection) | `extending.adoc` |
| Development / Cosmic layers / tooling | `architecture.adoc` |

## Verification strategy

This is a docs/tooling change, so "tests" are build + deploy checks, not pytest:

1. **Local build is green**: `make build-docs` produces `docs/build/site/index.html` with all nav
   pages and no Antora ERROR/WARN about missing xref targets.
2. **No Sphinx residue**: `grep -ri "sphinx" docs/ pyproject.toml .readthedocs.yml` returns nothing;
   the deleted files are gone; `make check-architecture` + `make test-all` still pass (proving the
   package is untouched).
3. **CI build is green** on the PR (the `build` job runs `make build-docs`).
4. **Deployment verified**: after merge to `master`, the `deploy` job succeeds and the Pages URL
   `https://meaningfy-ws.github.io/eds4jinja2/` serves the new site (HTTP 200, contains the site
   title and nav). RTD build (if it auto-triggers) is checked best-effort.
5. **Release** only after (4) is confirmed.

## Risks

- **Pages not enabled on the repo** → the `deploy` job fails. Mitigation: enable Pages
  (source = GitHub Actions) via `gh api` before/at first deploy; RTD remains a working fallback.
- **Local playbook `branches: [HEAD]` reads committed content only** (Antora reads the git worktree
  for HEAD in 3.1) — acceptable; document that uncommitted pages may need a commit to appear.
- **xref typos** break the build — caught by step 1/3 (Antora fails on missing xref targets).
