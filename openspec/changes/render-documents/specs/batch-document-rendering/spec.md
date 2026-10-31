## ADDED Requirements

### Requirement: Render a batch to memory
`ReportBuilder.render_documents(outputs, *, autoescape=None)` SHALL render the builder's configured
template once per entry of `outputs` (output name → template variables), passing the variables to
the template, and SHALL return a mapping of output name → rendered text in the iteration order of
`outputs.items()`. It SHALL write no file and SHALL call no rendering listener. The environment
globals (`conf`, the data-source builders, the helpers) SHALL stay available; a top-level template
variable whose name is a key of the environment globals SHALL be rejected with `ValueError` before
any render, while nested keys SHALL be allowed. A non-`str` output name, variables that are not a
`Mapping`, or a non-`str` variable name SHALL raise `TypeError` before any render.

#### Scenario: Two outputs from one template
- **GIVEN** a template package whose template prints `{{ name }}`
- **WHEN** `render_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}})` is called
- **THEN** it returns `{"a.txt": "A", "b.txt": "B"}`, the output folder holds no file and no listener ran

#### Scenario: A variable named conf
- **WHEN** `render_documents({"a.txt": {"conf": {}}})` is called
- **THEN** it raises `ValueError` and nothing is rendered

#### Scenario: A variable shadowing a data-source builder
- **WHEN** `render_documents({"a.txt": {"from_endpoint": "x"}})` is called
- **THEN** it raises `ValueError` naming `from_endpoint` and nothing is rendered

#### Scenario: A global name nested inside a variable
- **GIVEN** a template printing `{{ x.conf }}`
- **WHEN** `render_documents({"a.txt": {"x": {"conf": "C"}}})` is called
- **THEN** it returns `{"a.txt": "C"}`

#### Scenario: Wrong types
- **WHEN** an output name is not a `str`, its variables are not a `Mapping`, or a variable name is not a `str`
- **THEN** `TypeError` is raised and nothing is rendered

#### Scenario: Empty batch
- **WHEN** `render_documents({})` is called
- **THEN** it returns an empty mapping

### Requirement: Output names stay inside the output folder
Every output name SHALL resolve (`Path.resolve()`, following existing symlinks) to a path inside the
builder's output folder, other than the folder itself and other than an existing directory. No two
names of a batch SHALL resolve to the same path, and no name SHALL resolve to a parent folder of
another name's path. Sub-folders SHALL be allowed. A name that cannot be resolved (e.g. it contains a
NUL byte) SHALL be refused. Every refusal SHALL raise `ValueError` naming the output before anything
is rendered.

#### Scenario: Names that leave the folder
- **WHEN** an output is named `/tmp/x.txt`, `../x.txt`, `g/../../x.txt` or `.`
- **THEN** `ValueError` is raised naming it and no output is rendered

#### Scenario: Two names of the same file
- **WHEN** a batch names `a.txt` together with `./a.txt`, `g/../a.txt` or `a.txt/`
- **THEN** `ValueError` is raised naming both and no output is rendered

#### Scenario: A name that is the parent folder of another
- **WHEN** a batch names both `g` and `g/b.txt`, in either order
- **THEN** `ValueError` is raised naming `g` and no output is rendered

#### Scenario: A name of an existing directory
- **GIVEN** the folder `out/g` exists
- **WHEN** an output is named `g`
- **THEN** `ValueError` is raised naming it and no output is rendered

#### Scenario: A name with a NUL byte
- **WHEN** an output is named `"a.txt\x00"`
- **THEN** `ValueError` is raised naming it and no output is rendered

#### Scenario: A sub-folder
- **WHEN** `render_documents({"g/a.txt": {"name": "A"}})` is called
- **THEN** it returns `{"g/a.txt": "A"}`

### Requirement: Autoescape per batch
When `autoescape` is given, the batch SHALL be rendered with that autoescaping, and the builder's
environment SHALL keep its own setting, before and after the batch, also when rendering fails.

#### Scenario: Escaping on for one batch only
- **GIVEN** a default `ReportBuilder` (autoescape off) and a template printing `{{ name }}`
- **WHEN** `render_documents({"a.html": {"name": "<b>"}}, autoescape=True)` is called, then
  `render_documents({"a.txt": {"name": "<b>"}})`
- **THEN** the first returns `&lt;b&gt;`, the second `<b>`

#### Scenario: A plain batch, then an escaped one
- **GIVEN** a default `ReportBuilder` (autoescape off) and a template printing `{{ name }}`
- **WHEN** `render_documents` is called with `{"name": "<b>"}` plainly, then with `autoescape=True`,
  then plainly again
- **THEN** it returns `<b>`, `&lt;b&gt;`, `<b>`

#### Scenario: A failed escaped batch
- **GIVEN** a default `ReportBuilder` (autoescape off)
- **WHEN** a batch with `autoescape=True` raises during rendering, and a plain batch printing `<b>` follows
- **THEN** the plain batch returns `<b>` and `template_env.autoescape` is unchanged

### Requirement: Batch renders use the parallel pre-fetch
When the configuration sets `parallelism > 1`, each output of a batch SHALL be rendered through the
parallel pre-fetch with that output's variables, with the same all-or-nothing pre-warm as
`make_document()`. When the pre-warm fails, `render_documents` SHALL raise and return nothing. When
the record pass of an output fails, that output SHALL be rendered sequentially to memory, never
written.

#### Scenario: Parallel batch equals sequential batch
- **GIVEN** a data-dependent template package whose data source counts its fetches
- **WHEN** the same two-output batch is rendered with `parallelism` 1 and 4
- **THEN** both return the same texts
- **AND** with `parallelism` 4 each output's fetch ran exactly once, through the pre-warm

#### Scenario: Pre-warm failure
- **GIVEN** `parallelism` 4 and a data source whose fetch raises
- **WHEN** `render_documents` is called
- **THEN** it raises and returns no text

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
