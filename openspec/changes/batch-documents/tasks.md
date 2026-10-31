<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [ ]` checkboxes. -->

> Derives from: EPIC `batch-documents` (`proposal.md`); design in `design.md`. Every task is TDD.
> "Spec:" names the requirement in `specs/batch-document-rendering/spec.md` the task proves.

## 1. Render step

- [ ] 1.1 Extract the private render-to-text step (sequential and parallel, P-2); `make_document()`
  output and listener calls unchanged (Spec: make_document is unchanged)

## 2. Batch methods

- [ ] 2.1 `render_documents` with name and `conf` validation and autoescape restore (P-1, P-3, P-5;
  Spec: Render a batch to memory; Output names stay inside the output folder; Autoescape per batch)
- [ ] 2.2 `make_documents`: check all, then write all, listeners once (P-4; Spec: Make a batch)
- [ ] 2.3 Parallel path for batch renders, including the record-pass fallback to memory (P-2;
  Spec: Batch renders use the parallel pre-fetch)

## 3. Close

- [ ] 3.1 Docs: the two methods on the `ReportBuilder` page, with the example of design.md
- [ ] 3.2 Version 2.1.0 and CHANGELOG entry; `make check-all` green
- [ ] 3.3 PR; release only with the developer's go-ahead; archive the change

## Verification

`make check-all`; the existing `make_document` tests unchanged and green; `openspec validate
batch-documents --strict`.
