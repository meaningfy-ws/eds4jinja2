<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: EPIC `render-documents` (`proposal.md`); adds capability `batch-document-rendering`.

## Context

`ReportBuilder` (`eds4jinja2/services/report_builder.py`) loads `config.json`, builds
`template_env` with `conf` as a global, and exposes `make_document()`:

- sequential: before-listeners → `template.stream().dump(output_folder / template)` → after-listeners;
- `parallelism > 1`: wrap the data-source builders, record pass (`template.render()`), pre-warm,
  then the sequential path from the cache; if the record pass raises, restore the globals and run
  the sequential path.

Neither path accepts template variables or returns the text.

## Goals / Non-Goals

**Goals:** DEC-1 to DEC-5. **Non-Goals:** the EPIC's no-gos.

## Decisions

- **P-1 Signature.**
  ```python
  def render_documents(
      self, outputs: Mapping[str, Mapping[str, Any]], *, autoescape: bool | None = None
  ) -> dict[str, str]: ...
  ```
  `outputs` maps an output name to the variables of that render (`template.render(**variables)`);
  `conf` stays the environment global and a variable named `conf` is rejected (`ValueError`), so a
  template never sees two different `conf`. The result keeps the order of `outputs`. An empty
  `outputs` returns `{}`.
- **P-2 One private render step.** Extract `__render_text(variables) -> str` (sequential:
  `template.render(**variables)`; parallel: record pass with the same variables, pre-warm, render
  from cache; record-pass failure → restore globals, sequential `render`). `make_document()` keeps
  calling `stream().dump()` (byte-identical output, P-5). A parallel coordinator is created per output
  (each output may issue different queries).
- **P-3 Names (DEC-3).** Before rendering anything, every name is resolved as
  `(output_folder / name).resolve()` and must lie inside `output_folder.resolve()` and differ from it;
  otherwise `ValueError` naming the offending output. Two names resolving to the same path (`a.txt`,
  `./a.txt`) are refused too (found in review: the later write would silently replace the earlier).
  Sub-folders are allowed (`a/b.ttl`). The batch check is a private helper
  `__validated_output_paths(outputs) -> dict[name, Path]`, reused by `make-documents`.
- **P-4 Autoescape.** When `autoescape` is not `None`, the batch renders on
  `template_env.overlay(autoescape=…)`: it shares the globals (so the parallel wrapping applies) but
  has its own autoescape and compiled-template cache, so the builder's environment is never changed,
  on success or error. (Chosen in review over set-and-restore, which had to clear the shared cache
  because Jinja compiles autoescaping into the template.)
- **P-5 `make_document()` unchanged.** Same file, same bytes, same listener calls; the existing tests
  stay as they are and pass.

### Example

```python
builder = ReportBuilder(target_path="templates/diagram", output_path="out")
texts = builder.render_documents(
    {"diagram-g1.puml": {"view": g1}, "diagram-g2.puml": {"view": g2}}, autoescape=False
)
# {"diagram-g1.puml": "@startuml…", "diagram-g2.puml": "@startuml…"}; nothing in out/
```

## Error matrix

| Situation | Result |
|---|---|
| name absolute, `..` out of the folder, or the folder itself | `ValueError` naming it, before any render |
| a variable named `conf` | `ValueError` before any render |
| template raises during render | the exception propagates; autoescape restored |
| parallel record pass raises | logged warning, that output rendered sequentially (as today) |
| parallel pre-warm fails | the exception propagates (all-or-nothing, as today) |
| empty `outputs` | `{}` |

## Risks / Trade-offs

- **Conflict with `parallel-executor-hardening`** (reworks `__make_document_parallel`): P-2 isolates
  the parallel steps behind `__render_text`; whichever change lands second ports its part.
- All texts are held in memory; fine for documents, not for gigabyte reports (those keep
  `make_document()`, which streams).

## Open Questions

None.
