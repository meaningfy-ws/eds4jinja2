<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [ ] ` checkboxes. -->

> Derives from: EPIC `render-documents` ([proposal.md](proposal.md)); design in [design.md](design.md).
> Every task is TDD. "Spec:" names the requirement in
> [specs/batch-document-rendering/spec.md](specs/batch-document-rendering/spec.md) the task proves;
> the test for each scenario is listed in design.md "Test cases".

## 1. Render step

- [x] 1.1 Extract the shared parallel step `__with_prefetch(parallelism, env, variables, render)` and
  the in-memory `__render_text(env, variables)` (P-2); `make_document()` output and listener calls
  unchanged (Spec: make_document is unchanged)

## 2. Batch rendering

- [x] 2.1 `render_documents` with the shadowed-globals and type checks; the builder's environment is
  never changed, autoescape renders on an overlay (P-1, P-4; Spec: Render a batch to memory;
  Autoescape per batch)
- [x] 2.2 Batch validation `__validated_output_paths`: every name inside the folder, not a directory,
  no duplicates, no parent/child pair; returns name → path, reused by `make-documents` (P-3; Spec:
  Output names stay inside the output folder)
- [x] 2.3 Parallel path for batch renders, including the record-pass fallback to memory and the
  pre-warm failure (P-2; Spec: Batch renders use the parallel pre-fetch)

## 3. Close

- [x] 3.1 Docs: the method on the `ReportBuilder` page
  (`docs/modules/ROOT/pages/api-reference.adoc`), with the example of design.md
- [x] 3.2 CHANGELOG entry; `make check-all` green
- [ ] 3.3 PR (one PR with `make-documents`, branch `feature/batch-documents`)
- [ ] 3.4 Release 2.1.0 together with `make-documents` (DEC-7), on the developer's go-ahead
- [ ] 3.5 Archive the change after the release
- [ ] 3.6 Clarity-gate corrections applied (A.4 shadowed globals and B.10 types in code); gate
  re-run ≥9/10

## Verification

`make check-all`; the 2.0 `make_document` tests unchanged and green; `openspec validate
render-documents --strict`.
