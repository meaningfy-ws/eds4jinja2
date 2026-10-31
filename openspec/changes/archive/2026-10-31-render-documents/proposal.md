# EPIC: Render documents — one template, several named outputs, rendered to memory

## Appetite

**SMALL.** One method added to `ReportBuilder`, reusing the existing render paths (sequential and
parallel). `make_document()`, the CLI, the configuration format and the data sources stay as they are.

Seeds: `inputs/seed.md` (the request from rdf-fingerprinter). Followed by `make-documents`, which
writes what this change renders.

## Why

`make_document()` renders the configured template once, with no template variables, and streams it
straight to `output/<template name>`. A consumer that needs several texts from one template (one per
named graph) or needs the text in memory (to embed it, or to inspect it) has to bypass eds4jinja2 and
drive `template_env` itself, duplicating the render path and losing the parallel pre-fetch.
rdf-fingerprinter does exactly that today; its developer decided to extend eds4jinja2 instead.

## Solution outline

The outcome: **a consumer gets several named texts from one template package, in memory, through
eds4jinja2's own render path — sequential or parallel — with no file written.**

1. **Render a batch to memory.** The builder takes a mapping *output name → template variables*,
   renders its configured template once per entry with those variables, and returns *output name →
   text*.
2. **Same render path as `make_document()`.** Each output goes through the sequential render, or the
   parallel pre-fetch when `parallelism > 1`, including its fallback, which renders to memory too.
3. **Names that will be safe to write.** Output names are checked before anything renders: each
   stays inside the output folder, and no two names of a batch clash (same file, or one the parent
   folder of another). The follow-up `make-documents` and any caller can then write them without
   escaping the folder or losing an output.
4. **Autoescaping per batch**, for consumers rendering HTML and non-HTML from the same library.

## Key decisions

- **DEC-1**: A new method `ReportBuilder.render_documents`, not a change to `make_document()` —
  reason: no behaviour change for existing users (no-gos); rejected: optional parameters on
  `make_document()` (one method, two return shapes).
- **DEC-2**: One template per builder, several outputs — reason: a template package has one entry
  template (`config.json` → `template`); outputs differ by their variables and names only; rejected: a
  template name per output (no consumer needs it).
- **DEC-3**: Output names are relative file names inside the output folder; an absolute name or one
  that leaves the folder is rejected before anything is rendered — reason: names are built from data
  (a graph IRI) by consumers; rejected: trusting the caller.
- **DEC-4**: The parallel pre-fetch serves batch renders; its record-pass fallback renders to memory —
  reason: `parallelism` must mean the same for both entry points. Coordinate with the in-flight
  `parallel-executor-hardening` change, which reworks the same method: whichever lands second adapts
  to the other.
- **DEC-5**: Rendering runs no listener — reason: the listeners copy static files next to written
  output, and nothing is written here; rejected: running them per render.
- **DEC-6**: Autoescaping per batch is rendered on a Jinja overlay environment — reason: the
  builder's shared environment is never changed, so a batch cannot leak its setting into
  `make_document()` or another batch; rejected: setting and restoring `template_env.autoescape`
  (needs clearing the shared template cache, and changes state other callers see).
- **DEC-7**: Released together with `make-documents` as 2.1.0 — reason: the two changes are one
  consumer need (rdf-fingerprinter task 6.1); one minor version announces both methods.

## Rabbit-holes

- The parallel path today writes through `__render_to_output`; splitting "render" from "write" must
  leave `make_document()` byte-identical.
- A per-batch setting must not leak into the shared environment: the builder's environment is never
  changed (DEC-6).
- A template variable that shadows a data-source builder (`from_endpoint`) would silently bypass the
  parallel pre-fetch; such variables are refused.

## No-gos

- No change to `make_document()`, the CLI (`mkreport`), `config.json` or the data sources.
- No writing of files (that is `make-documents`), no per-output template, no async API.
- No breaking change; released as minor version 2.1.0, together with `make-documents` (DEC-7).

---

## What Changes

- `ReportBuilder.render_documents(outputs, *, autoescape=None) -> dict[str, str]`.
- The parallel path can render to memory (`__with_prefetch`); `make_document()` keeps writing as in 2.0.
- CHANGELOG entry and a docs section for the method.

## Capabilities

### New Capabilities
- `batch-document-rendering`: rendering one template package to several named outputs in memory.

### Modified Capabilities
<!-- none: parallel-report-executor's requirements hold for batch renders as they are -->

## Impact

- Code: `eds4jinja2/services/report_builder.py`; tests under `tests/unit/services/`.
- Docs: the `ReportBuilder` API page (`docs/modules/ROOT/pages/api-reference.adoc`).
- Consumers: rdf-fingerprinter renders its representations through it (with `make-documents`).
