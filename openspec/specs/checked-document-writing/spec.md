# checked-document-writing Specification

## Purpose
Writing a rendered batch to disk only after every output passes the caller's check:
`ReportBuilder.make_documents`, the exact bytes written, the returned paths and the listener calls.
Builds on `batch-document-rendering`. Origin: change `make-documents` (2.1.0).
## Requirements
### Requirement: Write a batch only when every output passes
`ReportBuilder.make_documents(outputs, *, check=None, autoescape=None)` SHALL validate and render
every output as `render_documents` does, call `check(name, text)` for every output in the iteration
order of `outputs.items()`, and only when every check returns SHALL write every text under the
builder's output folder at its output name, creating sub-folders. Each file SHALL be written as
UTF-8 with no newline translation, so its bytes are exactly the encoded text the check accepted. An
existing file at an output path SHALL be overwritten; other files in the folder SHALL be left
untouched. It SHALL return the written paths — absolute, resolved (symlinks in the output path
expanded) — in the iteration order of `outputs.items()`. When a check raises, that exception SHALL
propagate unchanged, no later check SHALL be called and no file SHALL be written. A check's return
value SHALL be ignored; `check=None` SHALL write without checking.

In the scenarios below the builder has `output_path="out"`, its template prints `{{ name }}`, and
`ok` is a check that returns `None`.

#### Scenario: All checks pass
- **WHEN** `make_documents({"a.txt": {"name": "A"}, "g/b.txt": {"name": "B"}}, check=ok)` is called
- **THEN** `out/a.txt` and `out/g/b.txt` hold `A` and `B`, and their absolute paths are returned in that order

#### Scenario: One check fails
- **GIVEN** an empty output folder
- **WHEN** `check` raises `SyntaxError("bad")` for `b.txt` in a batch of `a.txt`, `b.txt`, `c.txt`
- **THEN** that same `SyntaxError` object propagates, `check` was not called for `c.txt`, and no file exists

#### Scenario: No check
- **WHEN** `make_documents({"a.txt": {"name": "A"}})` is called without `check`
- **THEN** `out/a.txt` holds `A`

#### Scenario: Bytes on disk are the checked text
- **WHEN** a rendered text contains `\r\n` and `\n` line ends
- **THEN** the file's bytes equal the UTF-8 encoding of the text the check received

#### Scenario: An existing file
- **GIVEN** `out/a.txt` holds `old` and `out/keep.txt` holds `keep`
- **WHEN** `make_documents({"a.txt": {"name": "new"}})` is called
- **THEN** `out/a.txt` holds `new` and `out/keep.txt` still holds `keep`

### Requirement: Listeners run once per batch
The before-rendering listeners SHALL run once before the batch is rendered and the after-rendering
listeners once after its files are written, each called with the builder's `configuration_context`
as `make_document()` does. When rendering or a check fails, the after-rendering listeners SHALL NOT
run. A name or variable that `render_documents` refuses SHALL raise its `ValueError` or `TypeError`
before any listener runs and before any file is written. An empty batch SHALL return an empty list
and run no listener.

#### Scenario: Two outputs, one listener call each
- **GIVEN** a builder with one before-listener and one after-listener
- **WHEN** a batch of two outputs is made
- **THEN** each listener ran exactly once, with the builder's `configuration_context`

#### Scenario: A failed check
- **WHEN** a check raises
- **THEN** the before-listener ran once and the after-listener did not run

#### Scenario: A render failure
- **WHEN** the template raises while rendering the batch
- **THEN** the before-listener ran once, the after-listener did not run, and no file is written

#### Scenario: A refused name
- **WHEN** `make_documents({"../x.txt": {"name": "A"}})` is called
- **THEN** `ValueError` is raised, no listener ran and no file is written

#### Scenario: Empty batch
- **WHEN** `make_documents({})` is called
- **THEN** it returns `[]` and no listener ran

