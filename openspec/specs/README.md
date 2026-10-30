# Durable capability specs — THE TRUTH

`openspec/specs/<capability>/spec.md` is the merged, machine-validated truth for eds4jinja2:
the RFC-2119 SHALL requirements + Given/When/Then scenarios that survived `/opsx:archive`.

- **This is authority.** Anything under `.claude/` (incl. `MEMORY.md`) is a regenerable index; if
  it disagrees with these specs, the specs win.
- Deltas in `openspec/changes/<id>/specs/` merge **here** on archive — never hand-edit a merged
  spec to diverge from the change that produced it.
- Fills as changes are archived (`openspec/changes/archive/`). Validate shape with
  `make check-spec` (`openspec validate --all --strict`).
