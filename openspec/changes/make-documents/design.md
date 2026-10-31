<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: EPIC `make-documents` ([proposal.md](proposal.md)); adds capability
> `checked-document-writing` ([spec](specs/checked-document-writing/spec.md)). Builds on change
> [`render-documents`](../render-documents/design.md): reuses `__validated_output_paths` (its P-3)
> and `__render_batch` (its P-2).

## Context

After `render-documents`, `ReportBuilder.render_documents(outputs, *, autoescape)` returns
*name → text* in memory, with the batch validated first by `__validated_output_paths` (names inside
the output folder, no clashes, no shadowed globals, right types). Nothing in eds4jinja2 writes such a
batch, checks it, or runs the listeners for it.

## Goals / Non-Goals

**Goals:** DEC-1 to DEC-5 of the [EPIC](proposal.md#key-decisions). **Non-Goals:** the EPIC's
[no-gos](proposal.md#no-gos).

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
  A `ReportBuilder` method: the helpers it reuses are name-mangled.
- **P-2 Order (DEC-1, DEC-4).**
  1. empty `outputs` → return `[]`, no listener;
  2. `__validated_output_paths(outputs)` → its `TypeError`/`ValueError`, no listener, no file;
  3. before-listeners, once, each called with `configuration_context` (as `make_document()`);
  4. `__render_batch(outputs, autoescape)` (no second validation);
  5. `check(name, text)` for every output in the iteration order of `outputs.items()`; the first
     exception propagates, later checks are not called, nothing is written;
  6. write every text at its validated path, creating parent folders, with
     `Path.write_text(text, encoding="utf-8", newline="")` (DEC-5); an existing file at that path is
     overwritten, other files in the folder are untouched;
  7. after-listeners, once, with `configuration_context`;
  8. return the paths — absolute, resolved (symlinks in `output_path` expanded) — in the iteration
     order of `outputs.items()`.
- **P-3 The check (DEC-2).** Any callable; it refuses by raising. eds4jinja2 does not wrap or translate
  the exception, so the consumer sees its own error object. `check=None` writes without checking; a
  check's return value is ignored.

### Example

```python
builder = ReportBuilder(target_path="templates/shapes", output_path="out")
builder.make_documents(
    {"shapes-g1.ttl": {"view": g1}, "shapes-g2.ttl": {"view": g2}},
    check=lambda name, text: rdflib.Graph().parse(data=text, format="turtle"),
    autoescape=False,
)
# -> the absolute paths of out/shapes-g1.ttl and out/shapes-g2.ttl, written only if both parse
```

## Error matrix

| Situation | Result |
|---|---|
| a name, variable or type that `__validated_output_paths` refuses (outside the folder, same file, parent folder of another name, existing directory, below an existing file, shadowed global, wrong type) | its `ValueError`/`TypeError`; no listener; nothing written |
| template raises during render | the exception propagates; before-listeners ran; after-listeners not run; nothing written |
| `check` raises for one output | that exception object propagates; later checks not called; nothing written; after-listeners not run |
| a write fails (disk full, permission) | the `OSError` propagates; files written before it remain (no rollback — [no-go](proposal.md#no-gos)); after-listeners not run |
| empty `outputs` | `[]`; no listener |

## Anti-patterns

| Don't | Do | Why |
|---|---|---|
| write each file right after its check | check all, then write all | a failed check must leave no partial set (DEC-1) |
| run the after-listeners in a `finally` | run them only after the writes | they act on written output; nothing was written (DEC-4) |
| wrap or translate the consumer's exception | let it propagate as raised | the consumer matches on its own error type (P-3) |
| validate names after the before-listeners | validate first (P-2 step 2) | a refused batch must have no side effect |
| write with the locale encoding or platform newlines | `encoding="utf-8", newline=""` | the bytes on disk must be the text the check accepted (DEC-5) |

## Test cases

Unit tests in `tests/unit/services/test_report_builder_make_documents.py` (fixtures in
`tests/unit/services/conftest.py`).

| Spec scenario | Test |
|---|---|
| All checks pass | `test_all_checks_pass` |
| One check fails | `test_one_check_fails_nothing_written`, `test_checks_stop_at_the_first_failure`, `test_check_return_value_is_ignored` |
| No check | `test_no_check`, `test_utf8_text`, `test_autoescape_passed_through` |
| Bytes on disk are the checked text | `test_bytes_on_disk_are_the_checked_text` |
| An existing file | `test_existing_file_is_overwritten_and_others_untouched` |
| Two outputs, one listener call each | `test_listeners_once_per_batch`, `test_listeners_get_the_configuration_context` |
| A failed check | `test_failed_check_runs_no_after_listener` |
| A render failure | `test_render_failure_runs_no_after_listener` |
| A refused name | `test_refused_name_runs_no_listener`, `test_names_of_the_same_file_write_nothing`, `test_name_under_an_existing_file_writes_nothing` |
| (error matrix) a write fails | `test_failed_write_runs_no_after_listener` |
| Empty batch | `test_empty_batch` |

## Risks / Trade-offs

- Writes are not atomic ([rabbit-hole](proposal.md#rabbit-holes)): the guarantee is about checks, not
  about the disk. Everything predictable is refused before the first write (names that clash, sit
  under an existing file or name a directory), so only a disk-level error (full, permission, a file
  created concurrently) can leave a partial set.
- The before-listeners run before rendering, as in `make_document()`; when rendering or a check then
  fails they have run without output.
- `test_bytes_on_disk_are_the_checked_text` cannot fail on Linux (no newline translation there); it
  guards Windows, which CI does not run.
- A builder is not thread-safe (render-documents design, Risks); make one batch at a time per builder.

## Open Questions

None. Release: together with `render-documents` as 2.1.0 (`tasks.md` 2.5).
