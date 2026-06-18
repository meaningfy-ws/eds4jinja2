# eds4jinja2
An easy way to reports generation with Jinja2 templates. 

With Embedded Datasource Specifications inside Jinja2 templates, you can fetch the data you need on the spot. 

![test](https://github.com/meaningfy-ws/eds4jinja2/workflows/test/badge.svg)
[![codecov](https://codecov.io/gh/meaningfy-ws/eds4jinja2/branch/master/graph/badge.svg)](https://codecov.io/gh/meaningfy-ws/eds4jinja2)
[![Documentation Status](https://readthedocs.org/projects/eds4jinja2/badge/?version=latest)](https://eds4jinja2.readthedocs.io/en/latest/?badge=latest)

![PyPI](https://img.shields.io/pypi/v/eds4jinja2?color=teal&label=version)
![PyPI - Status](https://img.shields.io/pypi/status/eds4jinja2)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eds4jinja2)
![PyPI - License](https://img.shields.io/pypi/l/eds4jinja2?color=green)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/eds4jinja2)

Specify the data sources in your JINJA templates directly.

```jinja2
{% set content, error = from_file(path).fetch_tree() %} \n
content:  {{ content }}\n
error: {{ error }}\n
```

```jinja2
{% set content, error =
    from_endpoint(endpoint).with_query(query_string).fetch_tabular() %}
content:  {{ content }} \n
error: {{ error }} \n
```

# Installation

```shell script
pip install eds4jinja2
```

For the optional fast in-memory SPARQL engine (oxigraph), install the extra:

```shell script
pip install eds4jinja2[oxigraph]
```

# Usage

[Read the docs here](https://eds4jinja2.readthedocs.io/en/latest/)  

## In-memory graph data sources

Besides a remote SPARQL endpoint (`from_endpoint`) and tabular/RDF files, reports can be
rendered against an **in-process RDF graph** — no SPARQL server required. Two builders are
available in templates:

- `from_graph(graph)` — query an in-memory graph/store you already hold (an `rdflib.Graph`,
  a `pyoxigraph` store, or any `query(sparql)` callable). Alias: `from_memory`.
- `from_rdf(sources, engine="rdflib")` — load one or more RDF files/URLs into an in-memory
  graph once (engine: `"rdflib"` default, or `"oxigraph"`) and query it. Both tabular
  (`fetch_tabular`) and tree (`fetch_tree`) results are supported.

To render an **existing report against an in-memory graph with the templates unchanged**,
inject a builder that overrides `from_endpoint` (which the templates already call):

```python
import rdflib
from eds4jinja2 import InMemorySPARQLDataSource
from eds4jinja2.builders.report_builder import ReportBuilder

graph = rdflib.Graph().parse("dataset.ttl")  # the consumer owns loading/manipulation
ReportBuilder(
    "report/",
    external_data_source_builders={"from_endpoint": lambda _endpoint: InMemorySPARQLDataSource(graph)},
).make_document()
```

## Parallel report execution

For large reports whose runtime is dominated by SPARQL query latency, set `parallelism` in the
report `config.json` to pre-warm all data fetches concurrently before rendering:

```json
{ "template": "report.html", "conf": {}, "parallelism": 16 }
```

Execution is threads-only and **all-or-nothing** (any fetch failure aborts the report, no
partial output); results are staged in a temp folder that is cleaned up afterwards. With
`parallelism` unset or `1` the behaviour is exactly the previous sequential render. Threaded
speed-up is real for remote endpoints and oxigraph in-memory graphs (both release the GIL);
rdflib in-memory queries are GIL-bound (correct, limited speed-up).

## Contributing
You are more than welcome to help expand and mature this project. We adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your interactions on the project.   
When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the maintainers of this repository before making a change.

## Licence 
This project is licensed under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
Powered by [Meaningfy](https://github.com/meaningfy-ws).
