<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [ ] ` checkboxes. -->

> Derives from: EPIC `make-documents` ([proposal.md](proposal.md)); design in [design.md](design.md).
> Every task is TDD. "Spec:" names the requirement in
> [specs/checked-document-writing/spec.md](specs/checked-document-writing/spec.md) the task proves;
> the test for each scenario is listed in design.md "Test cases". Builds on
> [`render-documents`](../render-documents/design.md); both ship in one PR.

## 1. Checked writes

- [x] 1.1 `make_documents`: validate, render, check all, then write all as UTF-8 with `newline=""`,
  with sub-folders (P-1, P-2, P-3; Spec: Write a batch only when every output passes)
- [x] 1.2 Listeners once per batch, with `configuration_context`; none for a refused or empty batch;
  no after-listener after a failed render or check (P-2; Spec: Listeners run once per batch)

## 2. Close

- [x] 2.1 Docs: the method on the `ReportBuilder` page
  ([api-reference.adoc](../../../docs/modules/ROOT/pages/api-reference.adoc)), with the example of
  design.md
- [x] 2.2 Version 2.1.0 (with `render-documents`) and CHANGELOG entry; `make check-all` green
- [ ] 2.3 PR (one PR with `render-documents`, branch `feature/batch-documents`)
- [x] 2.4 Clarity-gate corrections applied (in code: write with `newline=""`; refuse a name that is
  the folder of another, names an existing directory or sits under an existing file) and the gate
  re-run at ≥9/10
- [ ] 2.5 Release 2.1.0 together with `render-documents` (DEC-6), on the developer's go-ahead
- [ ] 2.6 Archive the change after the release

## Verification

`make check-all`; `openspec validate make-documents --strict`.
