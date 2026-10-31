# EPIC: Batch documents — one template, several named outputs, rendered to memory or checked then written

## Appetite

**SMALL.** One capability added to `ReportBuilder` (two methods), reusing the existing render
paths. `make_document()`, the CLI, the configuration format and the data sources stay as they are.

Seeds: `inputs/seed.md` (the request from rdf-fingerprinter).

## Why

`make_document()` renders the configured template once, to `output/<template name>`, with no
template variables, and writes it unchecked. A consumer that needs several files from one template
(one per named graph), the text in memory, or a validity check before anything is written has to
bypass eds4jinja2 and drive `template_env` itself, duplicating the render path and losing the
parallel pre-fetch. rdf-fingerprinter does exactly that today; its developer decided to extend
eds4jinja2 instead.

## Solution outline

The outcome: **a consumer gets several named documents from one template package through
eds4jinja2's own render path, either in memory or written only after every one has passed the
consumer's check.**

1. **Render a batch to memory.** The builder takes a mapping *output name → template variables*,
   renders its configured template once per entry with those variables, and returns *output name →
   text*. Nothing is written; no listener runs.
2. **Make a batch.** The same render, then the consumer's check on every text, then all files are
   written under the builder's output folder. One failed check means no file is written. The
   rendering listeners run once for the batch.
3. **Same render path as `make_document()`.** Each output goes through the sequential render, or the
   parallel pre-fetch when `parallelism > 1`, including its fallback, which renders to memory too.
4. **Autoescaping per batch**, for consumers rendering HTML and non-HTML from the same library.

## Key decisions

- **DEC-1**: Two new methods on `ReportBuilder` (`render_documents`, `make_documents`), not a change
  to `make_document()` — reason: no behaviour change for existing users (no-gos); rejected: new
  optional parameters on `make_document()` (one method with two return shapes).
- **DEC-2**: One template per builder, several outputs — reason: a template package has one entry
  template (`config.json` → `template`); each output differs by its variables and name only;
  rejected: a template name per output (no consumer needs it).
- **DEC-3**: Check all, then write all — reason: a consumer must never see a partial set of files
  after a failed check; rejected: check-and-write per output.
- **DEC-4**: Output names are relative file names inside the output folder; an absolute name or one
  that leaves the folder is rejected before anything is rendered — reason: names are built from data
  (a graph IRI) by consumers; rejected: trusting the caller.
- **DEC-5**: The parallel pre-fetch serves batch renders; its record-pass fallback renders to memory
  instead of writing the file — reason: `parallelism` must mean the same for both entry points.
  Coordinate with the in-flight `parallel-executor-hardening` change, which reworks the same method:
  whichever lands second adapts to the other.

## Rabbit-holes

- The parallel path today writes through `__render_to_output`; splitting "render" from "write"
  must leave `make_document()` byte-identical.
- Listeners receive `configuration_context`; they must not be called once per output.
- Autoescape set on the shared environment stays set; restore it after the batch.

## No-gos

- No change to `make_document()`, the CLI (`mkreport`), `config.json` or the data sources.
- No per-output template, no streaming to disk, no async API.
- No breaking change; released as a minor version (2.1.0).

---

## What Changes

- `ReportBuilder.render_documents(outputs, *, autoescape=None) -> dict[str, str]`.
- `ReportBuilder.make_documents(outputs, *, check=None, autoescape=None) -> list[pathlib.Path]`.
- The parallel path renders to memory internally; `make_document()` keeps writing as today.
- Version 2.1.0, CHANGELOG entry, docs page for the two methods.

## Capabilities

### New Capabilities
- `batch-document-rendering`: rendering one template package to several named outputs, in memory or
  checked then written.

### Modified Capabilities
<!-- none: parallel-report-executor's requirements hold for batch renders as they are -->

## Impact

- Code: `eds4jinja2/services/report_builder.py`; tests under `tests/unit/services/`.
- Docs: the `ReportBuilder` API page.
- Consumers: rdf-fingerprinter 2.1 requires `eds4jinja2>=2.1,<3`.
