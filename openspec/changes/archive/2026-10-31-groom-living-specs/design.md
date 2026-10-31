<!-- PLAN (design half). PLAN = this file + tasks.md. -->

> Derives from: EPIC `groom-living-specs` ([proposal.md](proposal.md)).

## Context

`openspec/specs/` is the durable truth. After 2.1.0 three requirements were checked against the
code: two are false (DEC-1, the version requirement), one was untested (concurrent reads).

## Decisions

- **P-1** Spec deltas: REMOVED for the version requirement (with reason and migration); MODIFIED for
  the pre-warm requirement, carrying its full text with "by a record pass over the template and/or an
  explicit `prefetch` manifest" replaced by "by a record pass over the template", the first scenario
  renamed "Recorded queries are fetched before rendering", and "or manifest seeding" dropped from the
  cache-miss scenario.
- **P-2** Test `test_concurrent_reads_return_correct_results`: 8 threads released together by a
  barrier each run 11 different SELECTs twice against one rdflib store loaded with 200 subjects; every
  answer must equal the sequential answer.
- **P-3** `Purpose` lines are written directly in `openspec/specs/` — `openspec archive` asks for it
  ("Update Purpose after archive"); they are not requirements and carry no delta.
- **P-4** `parallel-executor-hardening`: add a "Closed" note to its proposal, then
  `openspec archive parallel-executor-hardening --skip-specs --yes`.

## Open Questions

None.
