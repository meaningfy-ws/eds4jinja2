# Seed: request from rdf-fingerprinter, 2026-10-31 (secondary; never groomed)

rdf-fingerprinter 2.1 renders one template package into several files: one SHACL shapes file and
one PlantUML diagram per named graph (`shapes-<graph>.ttl`, `diagram-<graph>.puml`), and an HTML
document that embeds the diagrams. `ReportBuilder.make_document()` cannot do that: it renders the
configured template once, to `output/<template name>`, without template variables, and writes the
file without letting the caller check it first. rdf-fingerprinter therefore bypasses it and renders
through `ReportBuilder.template_env` (its adapter `fingerprint/adapters/template_renderer.py`).

The developer's review of rdf-fingerprinter (2026-10-31) asked "how come we do not use eds4jinja
generators?" and decided: **extend eds4jinja2 upstream** so the documents are built by eds4jinja2.
The developer writes the implementation; this change carries the specification only.

What rdf-fingerprinter needs (its design P-6, `openspec/changes/domain-object-model/design.md`):

1. Render one template to several outputs, each with its own file name and template variables.
2. Render to memory (the HTML document embeds diagrams that are never written as files of its own).
3. Check every rendered text (rdf-fingerprinter parses the Turtle) before any file is written, so a
   failed check leaves no partial output.
4. Choose autoescaping per batch (on for HTML, off for Turtle and PlantUML).
5. Keep the parallel pre-fetch (`parallelism > 1`) working for these renders.
