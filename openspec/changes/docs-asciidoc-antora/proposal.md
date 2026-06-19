<!-- The EPIC — the shaped bet. In Meaningfy the EPIC *is* the OpenSpec proposal. -->

# EPIC: Migrate the documentation to AsciiDoc + Antora

## Appetite

**Medium.** Replace the Sphinx/reStructuredText doc stack with the Meaningfy house standard —
**AsciiDoc authored, built by Antora** — restructure the single `index.rst` dump into a small,
navigable, enriched multi-page site, wire the build into **GitHub Actions + `make` targets** (so
there is a local view), and publish to **GitHub Pages** (canonical) while keeping the existing
**ReadTheDocs** URL/badge alive from the same playbook. No library code change, no public-API
change, no new methodology — just better docs and a cleaner toolchain. One patch release captures it.

## Why

The current documentation is a single 385-line `docs/index.rst` (reStructuredText) rendered by
**Sphinx** with `sphinxcontrib.apidoc` autodoc, published on ReadTheDocs (`docs/conf.py`,
`.readthedocs.yml`). Three problems:

1. **Wrong toolchain for the house.** Every sibling Meaningfy project that maintains real docs
   (`mapping-suite-sdk`, `entity-resolution-docs`) authors **AsciiDoc** and builds with **Antora**;
   the global standard (`~/.claude/CLAUDE.md`) says *"we prefer AsciiDoc with an Antora setup."*
   `eds4jinja2` is the odd one out on Sphinx, so doc conventions, UI, and CI do not transfer.
2. **Poor information architecture.** Everything lives in one giant `index.rst` page — install,
   why, every data source, LaTeX syntax, CLI, `ReportBuilder` API, extending, architecture — with no
   navigation, no search, and `autodoc` configured to dump even **private members** (noise, not a
   reference). New users cannot find anything; the content has also drifted (it still references the
   pre-1.0 layout in places).
3. **Automation is opaque/external.** The only doc automation is ReadTheDocs building Sphinx on a
   webhook. There is **no `make` target and no GitHub Actions job** — a developer cannot build or
   preview the docs locally, and the build is invisible to PR CI.

The driver is consistency and usability: bring `eds4jinja2`'s docs onto the same AsciiDoc/Antora
rails as its siblings, make the build a first-class local + CI concern, and enrich the content into
a real site rather than one scrolling page.

## Solution outline

Five moves, all documentation/tooling only — **zero change to `eds4jinja2/`**:

1. **Adopt Antora + AsciiDoc.** Add `docs/antora.yml` (component definition), a production playbook
   `docs/antora-playbook.yml` and a local playbook `docs/antora-playbook.local.yml`, and a
   `package.json` pinning Antora 3.1 + the lunr search extension — copied from the proven
   `mapping-suite-sdk` / `entity-resolution-docs` setups.

2. **Restructure + enrich the content.** Split the monolith into a navigable
   `docs/modules/ROOT/pages/` tree (`index`, `getting-started`, `data-sources`, `in-memory-graphs`,
   `parallel-execution`, `templating`, `cli`, `api-reference`, `extending`, `architecture`) with a
   `nav.adoc`. Migrate every existing topic, fix the drift, and **enrich**: a curated public-API
   reference (replacing the private-member autodoc dump), a fail-safe `(content, error)` contract
   section, the data-source matrix, and an ASCII Cosmic-layer diagram.

3. **Local build + preview via `make`.** Add `build-docs`, `clean-docs`, `serve-docs`,
   `preview-docs`, `install-antora` targets (Node-based, modelled on the siblings) so a developer
   gets a local view of the site with one command.

4. **Build + publish in GitHub Actions.** A `docs.yml` workflow **builds the site on every PR**
   (validation) and **deploys to GitHub Pages on push to `master`** (`upload-pages-artifact` →
   `deploy-pages`). This is the "all automation in GitHub Actions" requirement.

5. **Keep ReadTheDocs alive from the same playbook.** Convert `.readthedocs.yml` to the Antora
   `build.jobs` form (Node 22 + `antora --fetch`) — the *same* AsciiDoc source feeds both targets, so
   the existing `readthedocs.io` badge/URL keeps working. This is the concrete answer to *"can we
   push AsciiDoc to both?"* — **yes**.

Then **remove the Sphinx stack** (`docs/conf.py`, `docs/index.rst`, `docs/srcdocs/`, `docs/Makefile`,
`docs/make.bat`) and the Python `docs` extra (Sphinx/myst/apidoc), since Antora is Node, not Python.

## Key decisions

- **DEC-1 (Antora + AsciiDoc, drop Sphinx)**: adopt the house toolchain rather than keep Sphinx.
  *(Alternatives: stay on Sphinx — rejected, off-standard, no UI/CI reuse; MkDocs/Markdown —
  rejected, also off-standard for Meaningfy.)*
- **DEC-2 (GitHub Pages canonical, ReadTheDocs kept as mirror)**: Pages via Actions satisfies the
  "all automation in GitHub Actions" ask and gives PR build validation; RTD is preserved at near-zero
  cost (reuse the same playbook via `build.jobs`) so the existing public URL/badge does not break.
  *(Alternatives: RTD-only like `mapping-suite-sdk` — rejected, leaves automation outside GitHub and
  gives no PR preview; Pages-only, retire RTD — rejected, breaks the existing `readthedocs.io` badge
  for no gain when keeping it is ~10 lines.)*
- **DEC-3 (curated API reference, not autodoc)**: hand-write a focused public-API page
  (`build_eds_environment`, `ReportBuilder`, the data-source builders, the `DataSource` contract)
  instead of porting `sphinxcontrib.apidoc`. The public surface is small; autodoc currently dumps
  private members — curation is higher quality and more maintainable. *(Alternative: find an
  AsciiDoc autodoc bridge — rejected, none is mature for Python; YAGNI.)*
- **DEC-4 (lunr search, ASCII layer diagram, no Mermaid)**: include the `@antora/lunr-extension`
  (real value, trivial) but render the Cosmic-layer diagram as an AsciiDoc literal block rather than
  pulling in the Mermaid extension — zero extra dependency for a single diagram. *(Alternative:
  Mermaid extension like `entity-resolution-docs` — deferred, not worth a dep for one diagram.)*
- **DEC-5 (docs/tooling only — no library change)**: nothing under `eds4jinja2/` is touched; the
  package code, tests, public API, and version-SSOT mechanism are untouched. The release is a
  documentation patch.
- **DEC-6 (verify the deployment, then release)**: merge → let Actions build and deploy → confirm the
  Pages site is live and correct → only then cut the release. The "deployment to verify" is the docs
  site, not PyPI.

## Rabbit-holes

- Do **not** rewrite or restyle the library code, the README's substance, or the methodology — only
  the docs site and its build.
- Do **not** build a custom Antora UI bundle/theme; use the stock `antora-ui-default` bundle the
  siblings use.
- Do **not** add Mermaid, PDF/EPUB output, or multi-version docs in this change (Antora `version: ~`
  single version, HTML only).
- Do **not** try to auto-generate API docs from docstrings; the curated page is the reference.
- Do **not** invent new content domains — migrate and tighten what exists; "enrich" means clarity,
  structure, examples, and fixing drift, not new features.

## No-gos

<!-- MANDATORY. Explicitly out of scope. -->

- **No change to `eds4jinja2/` package code, the public API, or behaviour.** Docs/tooling only.
- **No Sphinx/reStructuredText left behind** — the stack is fully removed, not run in parallel.
- **No custom Antora theme / UI bundle** — stock default UI only.
- **No Mermaid, no PDF/EPUB, no versioned (multi-branch) docs** in this change.
- **No docstring-driven autodoc** — the API reference is a curated AsciiDoc page.
- **No new runtime or test dependency** — the only new deps are Node dev-tools for the doc build
  (Antora + lunr), not part of the Python package.
- **No break** to the existing `readthedocs.io` URL/badge — RTD keeps building from the same source.

---

## What Changes

- Add the Antora scaffold under `docs/`: `antora.yml`, `antora-playbook.yml`,
  `antora-playbook.local.yml`, `package.json`, `modules/ROOT/nav.adoc`, and the `pages/*.adoc` tree.
- Migrate and enrich all current documentation content from `docs/index.rst` + `README.md` into the
  multi-page AsciiDoc site; replace autodoc with a curated public-API reference page.
- Add documentation `make` targets (`build-docs`, `clean-docs`, `serve-docs`, `preview-docs`,
  `install-antora`) and the Node vars they need; extend `.PHONY`.
- Add `.github/workflows/docs.yml`: build on PR, deploy to GitHub Pages on `master`.
- Convert `.readthedocs.yml` to the Antora `build.jobs` form (Node 22) so RTD builds the same source.
- Remove the Sphinx stack (`docs/conf.py`, `docs/index.rst`, `docs/srcdocs/`, `docs/Makefile`,
  `docs/make.bat`) and the Python `docs` extra (`Sphinx`, `myst-parser`, `sphinxcontrib-apidoc`) from
  `pyproject.toml`; drop `[docs]` from the `dev` extra.
- Update `.gitignore` (`docs/build/`, `node_modules/`) and the README "Documentation" section/badges
  to point at the Pages site (RTD kept as a mirror).
- Bump the patch version and add a CHANGELOG entry. **PATCH, docs-only.**

## Capabilities

### New Capabilities
- `documentation-site`: the project's published documentation is authored in AsciiDoc, built by
  Antora, buildable locally via `make`, built on every PR and deployed to GitHub Pages by GitHub
  Actions, and mirrored on ReadTheDocs from the same playbook.

### Modified Capabilities
<!-- None: no existing spec carries requirements for documentation. -->

## Impact

- **Code**: none under `eds4jinja2/`. New files under `docs/` (Antora + AsciiDoc), a new
  `.github/workflows/docs.yml`, `package.json`, edits to `Makefile`, `.readthedocs.yml`,
  `pyproject.toml`, `.gitignore`, `README.md`, `CHANGELOG.md`. Deletions: the Sphinx files above.
- **APIs**: none. No Python import path, signature, or config key changes.
- **Dependencies**: Python `docs` extra removed. New **Node dev-tooling** (Antora 3.1 + lunr) for
  building docs only — not shipped in the wheel/sdist.
- **Version**: PATCH bump (docs-only).
- **Golden thread / driver**: documentation consistency with the Meaningfy house standard
  (`mapping-suite-sdk`, `entity-resolution-docs`) and a first-class local + CI doc build.
