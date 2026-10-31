## ADDED Requirements

### Requirement: Write a batch only when every output passes
`ReportBuilder.make_documents(outputs, *, check=None, autoescape=None)` SHALL render every output as
`render_documents` does, call `check(name, text)` for every output, and only when every check returns
SHALL write every text as a UTF-8 file at its output name under the builder's output folder, creating
sub-folders, and return the written paths in the order of `outputs`. When a check raises, that
exception SHALL propagate unchanged and no file SHALL be written.

#### Scenario: All checks pass
- **WHEN** `make_documents({"a.txt": {"name": "A"}, "g/b.txt": {"name": "B"}}, check=ok)` is called
- **THEN** `out/a.txt` and `out/g/b.txt` hold `A` and `B`, and the two paths are returned in that order

#### Scenario: One check fails
- **WHEN** `check` raises `SyntaxError("bad")` for `b.txt`
- **THEN** `SyntaxError("bad")` propagates and neither `a.txt` nor `b.txt` exists

#### Scenario: No check
- **WHEN** `make_documents({"a.txt": {"name": "A"}})` is called without `check`
- **THEN** `out/a.txt` holds `A`

### Requirement: Listeners run once per batch
The before-rendering listeners SHALL run once before the batch is rendered and the after-rendering
listeners once after its files are written. When rendering or a check fails, the after-rendering
listeners SHALL NOT run. An empty batch SHALL return an empty list and run no listener.

#### Scenario: Two outputs, one listener call each
- **GIVEN** a builder with one before-listener and one after-listener
- **WHEN** a batch of two outputs is made
- **THEN** each listener ran exactly once

#### Scenario: A refused batch
- **WHEN** a check raises
- **THEN** the before-listener ran once and the after-listener did not run
