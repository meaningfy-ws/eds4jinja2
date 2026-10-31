<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: EPIC `make-documents` (`proposal.md`); adds capability `checked-document-writing`.
> Builds on change `render-documents` (`render_documents`, the private `__output_path`).

## Context

After `render-documents`, `ReportBuilder.render_documents(outputs, *, autoescape)` returns
*name → text* in memory, with names already checked to stay inside the output folder. Nothing in
eds4jinja2 writes such a batch, checks it, or runs the listeners for it.

## Goals / Non-Goals

**Goals:** DEC-1 to DEC-4. **Non-Goals:** the EPIC's no-gos.

## Decisions

- **P-1 Signature.**
  ```python
  def make_documents(
      self,
      outputs: Mapping[str, Mapping[str, Any]],
      *,
      check: Callable[[str, str], None] | None = None,
      autoescape: bool | None = None,
  ) -> list[pathlib.Path]: ...
  ```
- **P-2 Order (DEC-1, DEC-4).** before-listeners once → `render_documents(outputs, autoescape=…)` →
  `check(name, text)` for every output, in order (the first exception propagates; nothing written) →
  write every text as UTF-8 at `__output_path(name)`, creating parent folders → after-listeners once →
  the paths, in order. An empty `outputs` returns `[]` and runs no listener.
- **P-3 The check (DEC-2).** Any callable; it refuses by raising. eds4jinja2 does not wrap or translate
  the exception, so the consumer sees its own error type and message.

### Example

```python
builder = ReportBuilder(target_path="templates/shapes", output_path="out")
builder.make_documents(
    {"shapes-g1.ttl": {"view": g1}, "shapes-g2.ttl": {"view": g2}},
    check=lambda name, text: rdflib.Graph().parse(data=text, format="turtle"),
    autoescape=False,
)
# -> [Path("out/shapes-g1.ttl"), Path("out/shapes-g2.ttl")], written only if both parse
```

## Error matrix

| Situation | Result |
|---|---|
| a name or a `conf` variable `render_documents` refuses | its `ValueError`; nothing written; no listener |
| template raises during render | the exception propagates; nothing written; after-listeners not run |
| `check` raises for one output | that exception propagates; no file written; after-listeners not run |
| a write fails (disk full, permission) | the `OSError` propagates; files written before it stay (no-go: no rollback) |
| empty `outputs` | `[]`; no listener |

## Risks / Trade-offs

- Writes are not atomic (EPIC rabbit-hole): the guarantee is about checks, not about the disk.
- The before-listeners run before rendering, as in `make_document()`; when rendering then fails they
  have run without output. Same as today's `make_document()`.

## Open Questions

None.
