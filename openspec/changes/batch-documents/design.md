<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: EPIC `batch-documents` (`proposal.md`); adds capability `batch-document-rendering`.

## Context

`ReportBuilder` (`eds4jinja2/services/report_builder.py`) loads `config.json`, builds
`template_env` with `conf` as a global, and exposes `make_document()`:

- sequential: before-listeners → `template.stream().dump(output_folder / template)` → after-listeners;
- `parallelism > 1`: wrap the data-source builders, record pass (`template.render()`), pre-warm,
  then the sequential path from the cache; if the record pass raises, restore the globals and run
  the sequential path.

Neither path accepts template variables, an output name, a check or an autoescape choice.

## Goals / Non-Goals

**Goals:** DEC-1 to DEC-5. **Non-Goals:** the EPIC's no-gos.

## Decisions

- **P-1 Signatures.**
  ```python
  def render_documents(
      self, outputs: Mapping[str, Mapping[str, Any]], *, autoescape: bool | None = None
  ) -> dict[str, str]: ...

  def make_documents(
      self,
      outputs: Mapping[str, Mapping[str, Any]],
      *,
      check: Callable[[str, str], None] | None = None,
      autoescape: bool | None = None,
  ) -> list[pathlib.Path]: ...
  ```
  `outputs` maps an output name to the variables of that render (`template.render(**variables)`);
  `conf` stays the environment global and a variable named `conf` is rejected (`ValueError`), so a
  template never sees two different `conf`. The result keeps the order of `outputs`. An empty
  `outputs` returns `{}` / `[]` and runs no listener.
- **P-2 One private render step.** Extract `__render_text(variables) -> str` (sequential:
  `template.render(**variables)`; parallel: record pass with the same variables, pre-warm, render
  from cache; record-pass failure → restore globals, sequential `render`). `make_document()` keeps
  calling `stream().dump()` (byte-identical output, P-6); the batch methods call `__render_text`.
  The parallel coordinator is created per output (each output may issue different queries).
- **P-3 Names (DEC-4).** Before rendering anything, every name is resolved as
  `(output_folder / name).resolve()` and must be inside `output_folder.resolve()` and not equal to
  it; otherwise `ValueError` naming the offending output. Sub-folders are allowed (`a/b.ttl`); the
  writer creates them.
- **P-4 Check then write (DEC-3).** `make_documents`: before-listeners once → `render_documents` →
  `check(name, text)` for every output in order (the first exception propagates; nothing written) →
  write every file as UTF-8 → after-listeners once → return the paths in order. `render_documents`
  runs no listener (it writes nothing; listeners copy static files next to written output).
- **P-5 Autoescape.** When `autoescape` is not `None`, set `template_env.autoescape` for the batch
  and restore the previous value afterwards (also on error). Jinja caches compiled templates per
  autoescape setting through its environment, so the template is fetched after setting it.
- **P-6 `make_document()` unchanged.** Same file, same bytes, same listener calls; the existing
  tests stay as they are and pass.

### Example

```python
builder = ReportBuilder(target_path="templates/shapes", output_path="out")
builder.make_documents(
    {"shapes-g1.ttl": {"view": g1}, "shapes-g2.ttl": {"view": g2}},
    check=lambda name, text: rdflib.Graph().parse(data=text, format="turtle"),
    autoescape=False,
)
# -> [Path("out/shapes-g1.ttl"), Path("out/shapes-g2.ttl")], written only if both parse
texts = builder.render_documents({"diagram-g1.puml": {"view": d1}})  # {"diagram-g1.puml": "@startuml…"}
```

## Error matrix

| Situation | Result |
|---|---|
| name absolute, `..` out of the folder, or the folder itself | `ValueError` before any render; nothing written |
| a variable named `conf` | `ValueError` before any render |
| template raises during render | the exception propagates; nothing written; autoescape restored |
| `check` raises for one output | that exception propagates; no file written; after-listeners not run |
| parallel record pass raises | logged warning, that output rendered sequentially (as today) |
| parallel pre-warm fails | the exception propagates (all-or-nothing, as today); nothing written |
| empty `outputs` | `{}` / `[]`; no listener |

## Risks / Trade-offs

- **Conflict with `parallel-executor-hardening`** (reworks `__make_document_parallel`): P-2 isolates
  the parallel steps behind `__render_text`; whichever change lands second ports its part.
- Rendering all outputs before writing holds every text in memory; fine for documents, not for
  gigabyte reports (those keep `make_document()`, which streams).

## Open Questions

None.
