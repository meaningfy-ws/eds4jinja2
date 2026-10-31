<!-- PLAN (tasks half). PLAN = design.md + this file. The apply phase parses `- [ ] ` checkboxes. -->

> Derives from: EPIC `make-documents` (`proposal.md`); design in `design.md`. Every task is TDD.
> "Spec:" names the requirement in `specs/checked-document-writing/spec.md` the task proves.
> Starts after `render-documents` is merged.

## 1. Checked writes

- [ ] 1.1 `make_documents`: render, check all, then write all, with sub-folders (P-1, P-2, P-3; Spec:
  Write a batch only when every output passes)
- [ ] 1.2 Listeners once per batch; not after a refused batch (P-2; Spec: Listeners run once per batch)

## 2. Close

- [ ] 2.1 Docs: the method on the `ReportBuilder` page, with the example of design.md
- [ ] 2.2 Version 2.1.0 (with `render-documents`) and CHANGELOG entry; `make check-all` green
- [ ] 2.3 PR; release only with the developer's go-ahead; archive the change

## Verification

`make check-all`; `openspec validate make-documents --strict`.
