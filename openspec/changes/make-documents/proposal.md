# EPIC: Make documents — check every rendered output, then write them all

## Appetite

**SMALL.** One method added to `ReportBuilder` on top of `render_documents` (change
`render-documents`, a prerequisite). `make_document()`, the CLI and the configuration format stay as
they are.

Seeds: `inputs/seed.md` (the request from rdf-fingerprinter).

## Why

`make_document()` writes its output unchecked, and `render_documents` writes nothing. A consumer that
generates machine-read files (Turtle shapes, diagram sources) must refuse a broken file before it
reaches disk, and must never leave a partial set behind: a folder with two of three shape files is
worse than none. Today rdf-fingerprinter renders, checks and writes in its own adapter; with this
change eds4jinja2 does it, and the rendering listeners run as they do for `make_document()`.

## Solution outline

The outcome: **a consumer writes several named documents from one template package only when every
one of them passed its check, with the rendering listeners run once for the batch.**

1. **Make a batch.** Render every output as `render_documents` does, pass each text to the consumer's
   check, and only if all pass write them all under the output folder.
2. **Listeners once per batch**: the before-rendering listeners before the batch, the after-rendering
   listeners after the files are written — not per output, and not when nothing is written.
3. **The written paths are returned**, in the order of the outputs, so the consumer can report them.

## Key decisions

- **DEC-1**: Check all, then write all — reason: a consumer must never see a partial set of files
  after a failed check; rejected: check-and-write per output.
- **DEC-2**: The check is a callable `check(name, text)` that raises to refuse — reason: eds4jinja2
  knows no output format; the consumer brings its parser; rejected: a registry of named checks in
  eds4jinja2.
- **DEC-3**: A new method `ReportBuilder.make_documents`, built on `render_documents` — reason: one
  render path; `make_document()` stays as it is; rejected: a `check` parameter on `make_document()`.
- **DEC-4**: The after-rendering listeners do not run when a check fails — reason: they act on written
  output (copying static files beside it), and nothing was written; rejected: running them in a
  `finally`.

## Rabbit-holes

- Writing several files is not atomic; a disk error mid-batch can still leave some files. Checks
  are what this change guarantees, not transactional writes.
- Sub-folders in names must be created before writing.

## No-gos

- No transactional or temporary-folder writes, no rollback of files already on disk before the batch.
- No built-in format checks (Turtle, XML, …): the consumer passes its own.
- No change to `make_document()`, the CLI or `config.json`; no breaking change; a minor version.

---

## What Changes

- `ReportBuilder.make_documents(outputs, *, check=None, autoescape=None) -> list[pathlib.Path]`.
- CHANGELOG entry and a docs section for the method.

## Capabilities

### New Capabilities
- `checked-document-writing`: writing a rendered batch only after every output passes the caller's check.

### Modified Capabilities
<!-- none -->

## Impact

- Code: `eds4jinja2/services/report_builder.py`; tests under `tests/unit/services/`.
- Depends on: change `render-documents`.
- Consumers: rdf-fingerprinter writes its SHACL shapes (parsed as Turtle before writing) and diagrams
  through it.
