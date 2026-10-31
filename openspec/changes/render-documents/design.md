<!-- PLAN (design half). PLAN = this file + tasks.md. The clarity gate scores the pair (≥9/10). -->

> Derives from: EPIC `render-documents` ([proposal.md](proposal.md)); adds capability
> `batch-document-rendering` ([spec](specs/batch-document-rendering/spec.md)). Followed by
> [`make-documents`](../make-documents/design.md), which reuses `__validated_output_paths` and
> `__render_batch`.

## Context

`ReportBuilder` (`eds4jinja2/services/report_builder.py`) loads `config.json`, builds
`template_env` with `conf` as a global, and, in 2.0, exposes `make_document()`:

- sequential: before-listeners → `template.stream().dump(output_folder / template)` → after-listeners;
- `parallelism > 1`: wrap the data-source builders, record pass (`template.render()`), pre-warm,
  then the sequential path from the cache; if the record pass raises, restore the globals and run
  the sequential path.

Neither path accepts template variables or returns the text.

## Goals / Non-Goals

**Goals:** DEC-1 to DEC-6 of the [EPIC](proposal.md#key-decisions). **Non-Goals:** the EPIC's
[no-gos](proposal.md#no-gos).

## Decisions

- **P-1 Signature and contract (DEC-1, DEC-2, DEC-5).**
  ```python
  def render_documents(
      self, outputs: Mapping[str, Mapping[str, Any]], *, autoescape: bool | None = None
  ) -> dict[str, str]: ...
  ```
  `outputs` maps an output name to the variables of that render (`template.render(**variables)`).
  The result keeps the iteration order of `outputs.items()`. An empty `outputs` returns `{}`.
  Renders run no listener (DEC-5). Only top-level variable names are checked: a top-level name that
  is a key of `template_env.globals` (`conf`, the data-source builders, the helpers, Jinja's own
  globals) is refused with `ValueError`; nested keys (`{"x": {"conf": …}}`) are allowed. Reason: a
  variable shadowing a global wins over it in Jinja, so `conf` would differ from the configuration,
  and a shadowed `from_endpoint` is not wrapped, so the parallel pre-fetch is silently bypassed.
- **P-2 One render step, shared with `make_document()` (DEC-4).** `__with_prefetch(parallelism, env,
  variables, render)` holds the parallel path: wrap the builders in `env.globals`, record pass with
  `variables`, pre-warm, `render()` from the cache; record-pass failure → restore the globals and
  call `render()` sequentially. `make_document()` passes `__render_to_output` as `render` (it still
  streams with `stream().dump()`, P-5); a batch passes an in-memory render through
  `__render_text(env, variables)`. A new `FetchCoordinator` is created per output (outputs may issue
  different queries). `__render_batch(outputs, autoescape)` renders already-validated outputs.
- **P-3 Batch validation (DEC-3).** `__validated_output_paths(outputs) -> dict[str, Path]` runs
  before anything is rendered and returns name → path in iteration order. Per name it checks, in
  this order: types (P-1, `TypeError`); shadowed globals (P-1); `(output_folder / name).resolve()`
  lies inside `output_folder.resolve()` and differs from it; the path is not an existing directory
  and no folder above it is an existing file (its folder could not be created when written); no
  earlier name has the same path, and neither path is a parent folder of the other. Every
  refusal is a `ValueError` naming the output(s). Sub-folders are allowed (`a/b.ttl`). The helpers
  are name-mangled, so `make_documents` must stay a `ReportBuilder` method.
- **P-4 Autoescape per batch (DEC-6).** When `autoescape` is not `None`, the batch renders on
  `template_env.overlay(autoescape=…)`. With Jinja2 `>=3.1` (pinned `>=3.1.6,<4`) an overlay shares
  the parent's `globals` dict (so the parallel wrapping applies to it) and gets a new, empty template
  cache of the same size (`copy_cache`), so no template compiled with the other setting is reused.
  The builder's environment is never changed, on success or error. Rejected: set
  `template_env.autoescape` and restore it, which needs clearing the shared cache and changes state
  other callers see.
- **P-5 `make_document()` unchanged.** Same file, same bytes, same listener calls; the 2.0 tests stay
  as they are and pass.

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
| a non-`str` name, non-`Mapping` variables, a non-`str` variable name | `TypeError` before any render |
| a top-level variable named like an environment global (`conf`, `from_endpoint`, …) | `ValueError` naming it, before any render |
| name absolute, `..` out of the folder, or the folder itself | `ValueError` naming it, before any render |
| name of an existing directory | `ValueError` naming it, before any render |
| name below an existing file (`g/b.txt` while `out/g` is a file) | `ValueError` naming it, before any render |
| two names resolving to the same path (`a.txt`, `./a.txt`, `a.txt/`) | `ValueError` naming both, before any render |
| one name a parent folder of another (`g`, `g/b.txt`) | `ValueError` naming both, before any render |
| name that cannot be resolved (NUL byte, other OS error) | `ValueError` naming it, before any render |
| an existing symlink inside the folder pointing outside it | followed by `resolve()`, so refused as outside |
| names differing only in case | compared after `resolve()`, case-sensitively: two outputs (on a case-insensitive file system they are one file; not detected) |
| Windows drive-relative (`C:x`) or UNC (`\\host\share\x`) names | on Windows they resolve outside the folder and are refused; on POSIX they are ordinary relative names (CI runs Linux only) |
| template raises during render | the exception propagates; the builder's environment is never changed (P-4) |
| parallel record pass raises | logged warning, that output rendered sequentially to memory (`__with_prefetch`) |
| parallel pre-warm fails | `RuntimeError` propagates, nothing returned (all-or-nothing, as `make_document`) |
| empty `outputs` | `{}` |

## Anti-patterns

| Don't | Do | Why |
|---|---|---|
| set `template_env.autoescape` for a batch | render on `template_env.overlay(autoescape=…)` | the shared environment and its compiled-template cache stay untouched (P-4) |
| write a file in the record-pass fallback | call the caller's `render()` | a batch render writes nothing (DEC-5) |
| reuse one `FetchCoordinator` across outputs | one coordinator per output | outputs may issue different queries; caches must not leak between them |
| `stream().dump()` in the batch path | `template.render(**variables)` | the text is returned, not written |
| check names lexically (`".." in name`) | compare `Path.resolve()` results | `g/../a.txt`, `a.txt/`, symlinks and absolute names all resolve differently from their text |
| let a variable shadow a builder global | refuse it (P-1) | a shadowed builder is not wrapped; the pre-fetch is bypassed silently |

## Test cases

Unit tests in `tests/unit/services/test_report_builder_render_documents.py` (fixtures in
`tests/unit/services/conftest.py`).

| Spec scenario | Test |
|---|---|
| Two outputs from one template | `test_two_outputs_from_one_template`, `test_conf_global_stays_available` |
| A variable named conf | `test_variable_named_conf_is_refused` |
| A variable shadowing a data-source builder | `test_variable_shadowing_a_global_is_refused` |
| A global name nested inside a variable | `test_nested_global_name_is_allowed` |
| Wrong types | `test_wrong_types_raise_type_error_before_render` |
| Empty batch | `test_empty_batch` |
| Names that leave the folder | `test_names_that_leave_the_folder_are_refused` |
| Two names of the same file | `test_names_of_the_same_file_are_refused` |
| A name that is the parent folder of another | `test_name_that_is_a_parent_of_another_is_refused` |
| A name of an existing directory | `test_name_of_an_existing_directory_is_refused` |
| A name under an existing file | `test_name_under_an_existing_file_is_refused` |
| A symlink pointing outside the folder | `test_symlink_pointing_outside_is_refused` |
| A name with a NUL byte | `test_unreadable_name_is_refused_naming_it` |
| A sub-folder | `test_sub_folder_name` |
| Escaping on for one batch only | `test_autoescape_for_one_batch_only`, `test_autoescape_batch_leaves_shared_environment_untouched` |
| A plain batch, then an escaped one | `test_autoescape_batch_after_plain_batch` |
| A failed escaped batch | `test_plain_render_after_failed_autoescape_batch`, `test_autoescape_batch_error_leaves_environment_unchanged` |
| Parallel batch equals sequential batch | `test_parallel_batch_equals_sequential_batch`, `test_parallel_batch_fetches_once_per_output` |
| Pre-warm failure | `test_parallel_prewarm_failure_propagates` |
| Record-pass fallback stays in memory | `test_record_pass_fallback_stays_in_memory` |
| Existing reports | the unchanged 2.0 tests in `test_report_builder.py`, `test_report_builder_parallel.py`; plus `test_make_document_after_parallel_batch_still_writes` |

## Risks / Trade-offs

- **Collision with [`parallel-executor-hardening`](../parallel-executor-hardening/design.md).** Its
  design still targets `__make_document_parallel` (now `__with_prefetch`, the shared seam of
  `make_document` and batch renders) and removes the record-pass fallback (its P-7), which this
  spec requires for batch renders. Whichever change lands second rebases its design on
  `__with_prefetch` and writes a MODIFIED delta for "Batch renders use the parallel pre-fetch".
- **Not thread-safe.** `__with_prefetch` swaps `template_env.globals` while it runs (as 2.0's
  parallel path did); an overlay shares that dict. Run one batch at a time per builder.
- All texts are held in memory; fine for documents, not for gigabyte reports (those keep
  `make_document()`, which streams).

## Open Questions

None. Release: together with `make-documents` as 2.1.0 (`tasks.md` 3.5).
