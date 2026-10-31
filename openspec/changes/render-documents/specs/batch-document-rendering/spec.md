## ADDED Requirements

### Requirement: Render a batch to memory
`ReportBuilder.render_documents(outputs, *, autoescape=None)` SHALL render the builder's configured
template once per entry of `outputs` (output name → template variables), passing the variables to
the template, and SHALL return a mapping of output name → rendered text in the order of `outputs`.
It SHALL write no file and SHALL call no rendering listener. The `conf` global SHALL stay available;
a variable named `conf` SHALL be rejected with `ValueError` before any render.

#### Scenario: Two outputs from one template
- **GIVEN** a template package whose template prints `{{ name }}`
- **WHEN** `render_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}})` is called
- **THEN** it returns `{"a.txt": "A", "b.txt": "B"}`, the output folder holds no file and no listener ran

#### Scenario: A variable named conf
- **WHEN** `render_documents({"a.txt": {"conf": {}}})` is called
- **THEN** it raises `ValueError` and nothing is rendered

#### Scenario: Empty batch
- **WHEN** `render_documents({})` is called
- **THEN** it returns an empty mapping

### Requirement: Output names stay inside the output folder
Every output name SHALL resolve to a path inside the builder's output folder, other than the folder
itself, and no two names of a batch SHALL resolve to the same path; sub-folders SHALL be allowed.
Otherwise `ValueError` naming the output SHALL be raised before anything is rendered.

#### Scenario: Names that leave the folder
- **WHEN** an output is named `/tmp/x.txt`, `../x.txt` or `.`
- **THEN** `ValueError` is raised naming it and no output is rendered

#### Scenario: Two names of the same file
- **WHEN** a batch names both `a.txt` and `./a.txt`
- **THEN** `ValueError` is raised naming both and no output is rendered

#### Scenario: A sub-folder
- **WHEN** `render_documents({"g/a.txt": {"name": "A"}})` is called
- **THEN** it returns `{"g/a.txt": "A"}`

### Requirement: Autoescape per batch
When `autoescape` is given, the batch SHALL be rendered with that autoescaping, and the builder's
environment SHALL keep its own setting afterwards, also when rendering fails.

#### Scenario: Escaping on for one batch only
- **GIVEN** a template printing `{{ name }}` and an environment with autoescape off
- **WHEN** `render_documents({"a.html": {"name": "<b>"}}, autoescape=True)` is called, then
  `render_documents({"a.txt": {"name": "<b>"}})`
- **THEN** the first returns `&lt;b&gt;`, the second `<b>`

### Requirement: Batch renders use the parallel pre-fetch
When the configuration sets `parallelism > 1`, each output of a batch SHALL be rendered through the
parallel pre-fetch with that output's variables, with the same all-or-nothing pre-warm as
`make_document()`. When the record pass of an output fails, that output SHALL be rendered
sequentially to memory, never written.

#### Scenario: Parallel batch equals sequential batch
- **GIVEN** a data-dependent template package
- **WHEN** the same batch is rendered with `parallelism` 1 and 4
- **THEN** both return the same texts

#### Scenario: Record-pass fallback stays in memory
- **GIVEN** `parallelism` 4 and a template whose record pass raises
- **WHEN** `render_documents` is called
- **THEN** the text is returned and no file is written

### Requirement: make_document is unchanged
`make_document()` SHALL keep writing the configured template to `output/<template name>` with the
same content and the same listener calls as in 2.0.

#### Scenario: Existing reports
- **WHEN** the 2.0 `make_document` tests run against this version
- **THEN** they pass unchanged
