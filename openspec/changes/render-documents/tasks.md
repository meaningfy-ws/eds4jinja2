<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [ ] ` checkboxes. -->

> Derives from: EPIC `render-documents` (`proposal.md`); design in `design.md`. Every task is TDD.
> "Spec:" names the requirement in `specs/batch-document-rendering/spec.md` the task proves.

## 1. Render step

- [ ] 1.1 Extract the private render-to-text step (sequential and parallel, P-2); `make_document()`
  output and listener calls unchanged (Spec: make_document is unchanged)

## 2. Batch rendering

- [ ] 2.1 `render_documents` with `conf` rejection and autoescape restore (P-1, P-4; Spec: Render a
  batch to memory; Autoescape per batch)
- [ ] 2.2 Name check `__output_path` (P-3; Spec: Output names stay inside the output folder)
- [ ] 2.3 Parallel path for batch renders, including the record-pass fallback to memory (P-2; Spec:
  Batch renders use the parallel pre-fetch)

## 3. Close

- [ ] 3.1 Docs: the method on the `ReportBuilder` page, with the example of design.md
- [ ] 3.2 CHANGELOG entry; `make check-all` green
- [ ] 3.3 PR; release with `make-documents` or alone, as the developer decides; archive the change

## Verification

`make check-all`; the existing `make_document` tests unchanged and green; `openspec validate
render-documents --strict`.
