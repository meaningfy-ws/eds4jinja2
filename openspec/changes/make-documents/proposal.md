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
3. **The written paths are returned** (absolute, in the order of the outputs) so the consumer can
   report them.
4. **The bytes on disk are the text that was checked**: UTF-8, no newline translation.

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
- **DEC-5**: Files are written as UTF-8 with `newline=""` — reason: a check parses the text in
  memory; the file must hold exactly those bytes on every platform; rejected: the platform default
  (Windows would write `\r\n` for `\n`, and the locale encoding may not be UTF-8).
- **DEC-6**: Released together with `render-documents` as 2.1.0 — reason: one consumer need
  (rdf-fingerprinter task 6.1), one minor version.

## Rabbit-holes

- Writing several files is not atomic; a disk error mid-batch can still leave some files. Checks
  are what this change guarantees, not transactional writes.
- Sub-folders in names must be created before writing.
- Two names can point to one file (`a.txt`, `./a.txt`), one name can be the folder of another
  (`g`, `g/b.txt`), or a name can sit under an existing file (`g/b.txt` while `out/g` is a file);
  `render-documents` refuses all three before anything runs, so neither a lost output nor a
  predictable mid-batch write failure can occur.

## No-gos

- No transactional or temporary-folder writes, no rollback of files already on disk before the batch.
- No built-in format checks (Turtle, XML, …): the consumer passes its own.
- No change to `make_document()`, the CLI or `config.json`; no breaking change; minor version 2.1.0
  (DEC-6).

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
