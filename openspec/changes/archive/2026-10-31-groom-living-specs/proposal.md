# EPIC: Groom the living specs — make openspec/specs/ true of the code again

## Appetite

**SMALL.** Spec-only, plus one test. No production code changes.

## Why

A review of the durable specs after 2.1.0 (2026-10-31) found two requirements that are false of
the code and one that was never verified:

- `cosmic-layer-restructure` requires "VERSION reads 1.0.0"; the package is 2.1.0. That requirement
  recorded a one-off bump, not a behaviour.
- `parallel-report-executor` promises an optional `prefetch` manifest in `config.json`. It was never
  built (no code reads a `prefetch` key), although the archived change's tasks were ticked.
- `builtin-graph-store` requires stores to be safe for concurrent reads; nothing tested it.

Five specs also still carry the `Purpose: TBD` placeholder left by `openspec archive`.

## Solution outline

1. Remove the version requirement from `cosmic-layer-restructure` (versioning is release policy;
   `make check-version` keeps `VERSION` and `pyproject.toml` in sync).
2. Restate the pre-warm requirement of `parallel-report-executor` without the manifest: units are
   discovered by the record pass only.
3. Prove the concurrent-read requirement with a test against a loaded rdflib store.
4. Write the `Purpose` of every spec that still says TBD.
5. Close the in-flight change `parallel-executor-hardening` without implementing it (DEC-3).

## Key decisions

- **DEC-1**: Remove the manifest from the spec, not build it — reason: no consumer asks for it, and
  the record pass plus live cache misses already handle data-dependent templates; rejected: building
  it (YAGNI). Same conclusion as `parallel-executor-hardening` DEC-4.
- **DEC-2**: Keep the capability name `cosmic-layer-restructure` — reason: renaming moves a spec
  path and breaks links for no behaviour gain; rejected: renaming it to a behaviour name now.
- **DEC-3**: Close `parallel-executor-hardening` unimplemented — reason: 0 of 22 tasks done, no
  consumer asks for waves, per-source limits or run stats, and its design predates 2.1.0 (it targets
  `__make_document_parallel`, now `__with_prefetch`, and removes the record-pass fallback that
  `batch-document-rendering` requires). Its only part still needed — removing the manifest from the
  spec — is DEC-1 here. It is archived with `--skip-specs` and marked closed, so its analysis stays
  findable; it can be re-shaped as a new change if a need appears.

## Rabbit-holes

- A MODIFIED requirement must carry the full updated text, not a fragment.
- rdflib's thread safety is not documented; the test proves the queries this library issues, not
  every rdflib operation.

## No-gos

- No production code change, no new feature, no capability rename.
- No implementation of anything from `parallel-executor-hardening`.

---

## What Changes

- `cosmic-layer-restructure`: REMOVED "The version is bumped to 1.0.0 to signal the breaking move".
- `parallel-report-executor`: MODIFIED "Pre-warm fetches in parallel, then render from cache"
  (manifest wording removed).
- A concurrent-read test in `tests/unit/adapters/test_graph_store.py`.
- `Purpose` written for five specs; `parallel-executor-hardening` closed.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `cosmic-layer-restructure`: drops the 1.0.0 version requirement.
- `parallel-report-executor`: drops the `prefetch` manifest.

## Impact

- Docs/specs only, plus one test. No release needed.
