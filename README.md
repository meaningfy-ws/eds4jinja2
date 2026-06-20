# eds4jinja2

**Embed the data-source specification directly in your Jinja2 templates.** Declare *how* to fetch
the data inside the template, and eds4jinja2 resolves it at render time — so you build dynamic,
data-driven reports (HTML, LaTeX/PDF, or any text format) from SPARQL endpoints, in-memory RDF
graphs, and tabular/JSON files **without writing data-loading glue code**.

[![test](https://github.com/meaningfy-ws/eds4jinja2/actions/workflows/main.yml/badge.svg)](https://github.com/meaningfy-ws/eds4jinja2/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/meaningfy-ws/eds4jinja2/branch/master/graph/badge.svg)](https://codecov.io/gh/meaningfy-ws/eds4jinja2)
[![docs](https://github.com/meaningfy-ws/eds4jinja2/actions/workflows/docs.yml/badge.svg)](https://meaningfy-ws.github.io/eds4jinja2/)

![PyPI](https://img.shields.io/pypi/v/eds4jinja2?color=teal&label=version&cacheSeconds=3600)
![PyPI - Status](https://img.shields.io/pypi/status/eds4jinja2?cacheSeconds=3600)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eds4jinja2?cacheSeconds=3600)
![PyPI - License](https://img.shields.io/pypi/l/eds4jinja2?color=green&cacheSeconds=3600)

## Why eds4jinja2?

Generating a report usually tangles two jobs: **fetching the data** (Python code that queries
endpoints, reads files, shapes DataFrames and assembles a context dict) and **presenting it** (a
template). Every change to *what the report shows* forces a round-trip through the Python code.

eds4jinja2 collapses that coupling: **the template itself declares its data sources.** Your Python
code merely points the engine at a template and renders it — it stays agnostic of what data the
report displays.

This pays off when you:

- iterate quickly on report content and queries — change the **template**, not the code;
- want queries and their visualisation to live together and evolve together;
- build many report variants over the same data;
- need the same report to run against a **live SPARQL endpoint** *or* an **in-process graph** with
  no code change.

**Problems it solves**

- ❌ bespoke context-building / data-plumbing code for every report → ✅ none.
- ❌ queries in Python, layout in templates, drifting apart → ✅ co-located and easy to change.
- ❌ one source per report → ✅ one template, many heterogeneous sources (endpoint + file + graph).
- ❌ "needs a running SPARQL server" → ✅ query an in-memory `rdflib`/`oxigraph` graph, server-less.
- ❌ slow, query-bound reports → ✅ opt-in parallel pre-fetch.

## How it works

eds4jinja2 adds **data-source builders** as Jinja globals. In a template you call one, optionally
set a query, and fetch. Every fetch returns a fail-safe `(content, error)` pair — a failure is
surfaced *into* the template rather than crashing the render:

```jinja
{% set rows, error = from_endpoint(endpoint).with_query("SELECT * WHERE { ?s ?p ?o } LIMIT 10").fetch_tabular() %}
{% set tree, error = from_file("config.json").fetch_tree() %}
```

`fetch_tabular()` returns a pandas `DataFrame`; `fetch_tree()` returns a nested dict (JSON /
SPARQL-JSON). The data context is generated *during* rendering, so `template.render()` needs no
pre-built context.

## Installation

```shell
pip install eds4jinja2
# optional fast in-memory SPARQL engine (oxigraph):
pip install eds4jinja2[oxigraph]
```

Requires Python 3.11+.

## Quick start

**A. Render a template through the eds4jinja2 environment**

```python
from jinja2 import DictLoader
from eds4jinja2 import build_eds_environment

env = build_eds_environment(loader=DictLoader({
    "report.txt": "{% set rows, err = from_file('data.csv').fetch_tabular() %}"
                  "Rows: {{ rows | length }}\n{{ rows.to_string() }}",
}))
print(env.get_template("report.txt").render())   # data is fetched while rendering
```

**B. Drive a whole report folder with the `mkreport` CLI**

```shell
mkreport --target ./report --output ./out
```

The target folder follows a small convention:

```
report/
├── config.json     # { "template": "main.html", "conf": { "default_endpoint": "...", ... } }
├── templates/      # main.html and any includes
└── static/         # css/js/images, copied into the output (tree preserved)
```

`config.json` names the entry template and carries a `conf` object of variables available to all
templates. Set `"template_flavour_syntax": "latex"` for LaTeX templates.

## Data sources

| builder | source | `fetch_tabular` | `fetch_tree` |
|---|---|:--:|:--:|
| `from_file(path)` | CSV/TSV/Excel and JSON/YAML/TOML files | ✅ | ✅ |
| `from_endpoint(url)` | a remote SPARQL endpoint | ✅ | ✅ |
| `from_graph(graph)` (alias `from_memory`) | an in-process `rdflib.Graph`, `pyoxigraph` store, or `query(sparql)` callable | ✅ | ✅ |
| `from_rdf(sources, engine="rdflib")` | RDF file(s)/URL(s) loaded into an in-memory graph (`rdflib` or `oxigraph`) | ✅ | ✅ |
| `from_rdf_file(path)` | a single RDF file (legacy; superseded by `from_rdf`) | ✅ | — |

## In-memory graph data sources

Render reports against an **in-process RDF graph** — no SPARQL server required:

- `from_graph(graph)` (alias `from_memory`) — query an `rdflib.Graph`, a `pyoxigraph` store, or any
  `query(sparql)` callable you already hold.
- `from_rdf(sources, engine="rdflib")` — load one or more RDF files/URLs into an in-memory graph
  once (engine `"rdflib"` default, or `"oxigraph"`) and query it; tabular and tree results.

To render an **existing report against an in-memory graph with the templates unchanged**, inject a
builder that overrides `from_endpoint` (which the templates already call):

```python
import rdflib
from eds4jinja2 import InMemorySPARQLDataSource
from eds4jinja2.services.report_builder import ReportBuilder

graph = rdflib.Graph().parse("dataset.ttl")  # the consumer owns loading / manipulation
ReportBuilder(
    "report/",
    external_data_source_builders={"from_endpoint": lambda _endpoint: InMemorySPARQLDataSource(graph)},
).make_document()
```

## Parallel report execution

For large reports whose runtime is dominated by SPARQL query latency, set `parallelism` in the
report `config.json` to pre-fetch all data concurrently before rendering:

```json
{ "template": "report.html", "conf": {}, "parallelism": 16 }
```

Execution is threads-only and **all-or-nothing** (any fetch failure aborts the report, no partial
output); results are staged in a temp folder that is cleaned up afterwards. With `parallelism`
unset or `1` the behaviour is exactly the previous sequential render. Threaded speed-up is real for
remote endpoints and `oxigraph` in-memory graphs (both release the GIL); `rdflib` in-memory queries
are GIL-bound (correct, limited speed-up).

## Documentation

Full documentation (concepts, getting started, every data source, the `ReportBuilder` API, extending
with new data sources, architecture) is authored in AsciiDoc, built with Antora and published to
GitHub Pages: **https://meaningfy-ws.github.io/eds4jinja2/**

Build and preview it locally with `make preview-docs` (needs Node.js).

## Contributing

You are more than welcome to help expand and mature this project. We adhere to the
[Apache code of conduct](https://www.apache.org/foundation/policies/conduct); please follow it in
all your interactions on the project. When contributing, please first discuss the change you wish
to make via an issue, email, or another method with the maintainers before making a change.

## Licence

This project is licensed under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
Powered by [Meaningfy](https://github.com/meaningfy-ws).
