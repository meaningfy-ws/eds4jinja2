## MODIFIED Requirements

### Requirement: Batch renders use the parallel pre-fetch
When the configuration sets `parallelism > 1`, a batch SHALL be pre-fetched once: every output's
record pass SHALL run with that output's variables, the union of their fetches SHALL be pre-warmed in
one all-or-nothing parallel step, and every output SHALL then be rendered from that cache, so a fetch
shared by several outputs runs once for the batch. With `parallelism` unset or `1`, identical fetches
across the outputs of a batch SHALL also run once. When the pre-warm fails, `render_documents` SHALL
raise and return nothing. When the record pass of one output fails, a warning SHALL be logged, the
other outputs SHALL still be pre-warmed, and that output SHALL be rendered to memory with its
unrecorded fetches run live, never written.

#### Scenario: Parallel batch equals sequential batch
- **GIVEN** a data-dependent template package whose data source counts its fetches
- **WHEN** the same two-output batch is rendered with `parallelism` 1 and 4
- **THEN** both return the same texts

#### Scenario: A fetch shared by the outputs runs once
- **GIVEN** a template whose one query does not depend on the output's variables, and a data source that counts its fetches
- **WHEN** a batch of three outputs is rendered, with `parallelism` 4 and with `parallelism` 1
- **THEN** in each case the query was executed once

#### Scenario: Pre-warm failure
- **GIVEN** `parallelism` 4 and a data source whose fetch raises
- **WHEN** `render_documents` is called
- **THEN** it raises and returns no text

#### Scenario: Record-pass fallback stays in memory
- **GIVEN** `parallelism` 4 and a template whose record pass raises
- **WHEN** `render_documents` is called
- **THEN** the text is returned, a "record pass failed" warning is logged and no file is written

#### Scenario: One output's record pass fails
- **GIVEN** `parallelism` 4, a counting data source and a batch of two outputs where only the second output's record pass raises
- **WHEN** `render_documents` is called
- **THEN** both texts are returned and the first output's query was executed once, through the pre-warm

### Requirement: make_document is unchanged
`make_document()` SHALL keep writing the configured template to `output/<template name>` with the
same content and the same listener calls as in 2.0, for data sources that return the same result for
the same query within one render.

#### Scenario: Existing reports
- **WHEN** the 2.0 `make_document` tests run against this version
- **THEN** they pass unchanged
