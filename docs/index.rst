.. eds4jinja2 documentation master file


Embedded Datasource Specification in Jinja2 templates (v. |release|)
============================================================================

.. toctree::
    :maxdepth: 2

    srcdocs/modules

An easy way to reports generation with Jinja2 templates. With Embedded Datasource Specifications inside Jinja2 templates, you can fetch the data you need on the spot.

You can specify the file data source in your JINJA templates as follows. The *path* can be specified as absolute or
relative to the running script.

.. code-block:: Jinja

    {% set content, error = from_file(path).fetch_tree() %}
    content:  {{ content }}
    error: {{ error }}

In case you need to fetch data from a SPARQL endpoint, define a sparql_endpoint (usually in the global configuration)
and a custom sparql query_text. Use them in the template like this:

.. code-block:: Jinja

    {% set query_string = "select * where {?s ?p ?o} limit 10" %}
    {% set content, error =
        from_endpoint(endpoint).with_query(query_string).fetch_tabular() %}
    content:  {{ content }}
    error: {{ error }}

Currently supported data sources are:

* ``from_file`` - tabular (CSV, Excel, etc.) and tree-structured (JSON, YAML, etc.) files
* ``from_endpoint`` - a remote SPARQL endpoint, through a select query or describe request
* ``from_graph`` (alias ``from_memory``) - an in-process RDF graph you already hold (an
  ``rdflib.Graph``, a ``pyoxigraph`` store, or any ``query(sparql)`` callable); no server needed
* ``from_rdf`` - load one or more RDF files/URLs into an in-memory graph (engine ``rdflib`` by
  default, or ``oxigraph``) and query it; both tabular and tree results
* ``from_rdf_file`` - a single RDF file queried with SPARQL (tabular only; superseded by ``from_rdf``)

See `Capabilities`_ and `Extending eds4jinja2`_ below.

Not yet supported data sources are:

* from a XML file
* from a REST API
* from a relational database
* from a NoSQL database, e.g. MongoDB
* from a graph database, e.g. TinkerPop, Neo4j


But why?
#####################################
Imagine, for example, that you need to build a report from multiple SPARQL endpoints
and a configuration data provided in a local JSON file.


What you would normally do is retrieve first all the data and then pass it to the rendered template.

Alternatively, with **eds4jinja2** you can simply specify how the data shall be retrieved and then
just use it in the template.

1. instantiate the template from eds4jinja2 environment

.. code-block:: py3

    from eds4jinja2.services.jinja_builder import build_eds_environment
    from jinja2 import PackageLoader

    loader=PackageLoader('your_application', 'templates')
    env = build_eds_environment(loader=loader)


2. create a template file 'mytemplate.txt' that looks like this

.. code-block:: jinja

    {% set config_content, error = from_file("path/to/the/config/file.json").fetch_tree() %}
    The configuration content:
    {{ config_content }}

    {% set query_string = "select * where {?s ?p ?o} limit 10" %}
    {% set endpoint_content, error = from_endpoint(endpoint).with_query(query_string).fetch_tree() %}
    content: {{ endpoint_content }}
    error: {{ error }}

3. render the template with no context. The context is dynamically generated during the template rendering. Bingo!

.. code-block:: py3

    rendered_text = template.render()


So, what are the benefits?
####################################################

* your python code is agnostic of what data the template displays
* data fetching functionality is no longer part of the python context-building logic
* the queries and the template to visualise the query result set are tightly coupled and easy to modify
* this allows for building quickly custom visualisation templates (or modifying existent ones), before you even decide what the final query looks like

:code:`ReportBuilder` class usage
####################################################
:code:`ReportBuilder` accepts these parameters when instantiating:

:code:`target_path` (required) - the folder where the required resources are found.

:code:`config_file` (optional) - the name of the configuration file (defaults :code:`config.json`).

:code:`output_path` (optional) - the output folder where the result of the rendering will be created.

:code:`additional_config` (optional) - additional config parameters that are added to the default ones and are overwritten (deep update) in the project :code:`config.json`.

:code:`external_data_source_builders` (optional) - a mapping of extra/overriding data-source builders, merged *over* the defaults, so a consumer can override e.g. ``from_endpoint`` to serve an in-memory graph (see `In-memory graph data sources`_). Empty/None reproduces the default behaviour exactly.

:code:`external_filters` (optional) - a mapping of extra/overriding Jinja filters, merged over the defaults.

Example:

.. code-block:: py3

    target_path = 'some/path/for/template'
    config_file = 'other.json'
    output_path = 'some/other/path'
    additional_config = {"default_endpoint": 'http://localhost:9999'}
    report_builder = ReportBuilder(target_path=location,
                                   config_file=config_file,
                                   output_path=output_path,
                                   additional_config=additional_config)

CLI Usage
####################################################

The command to run the report generation is `mkreport`

The command line interface has three arguments:
########################################################################################################

* **--target** (optional): the directory where eds4jinja2 will load the content from, for rendering a template; this directory has a mandatory layout (see below)
* **--output** (optional): the directory where eds4jinja2 will place the rendered output; if this parameter is not specified, it will be placed in an "output" subdirectory that will be created where the "--target" parameter points to
* **--config** (optional): the name of the configuration file from where eds4jinja2 will load the configuration that's passed to Jinja2; default "config.json"

Example:

.. code-block:: bash

    mkreport --target=template --output=report_location --config=report_config.json

Target directory layout:
########################################################################################################
By convention, the target directory **must** contain:

#. a configuration file in JSON format which serves two purposes:

    * it specifies the main template for eds2jinja to start with (this template may refer to other additional templates)
    * it specifies a list of variables needed to render the aforementioned template(s); the list may contain anything you need in your templates

#. a directory named "templates" where all of your templates reside
#. if your template(s) need additional static resources (such as CSS/JS/etc files) a directory named "static" where all of these resources must reside; the contents of this directory will be copied to the output folder and its tree structure preserved


Example:

.. code-block:: json

    {
        "template": "main.html",
        "template_flavour_syntax": "html",
        "conf":
        {
            "default_endpoint" : "http://example.com/path/sparqlendpoint",
            "title": "Pretty printed relevant information",
            "type": "report",
            "author": "Your name here"
            "nexted_properties": {
                "graph": "http://publications.europa.eu/resources/authority/lam/DocumentProperty"
            },
        }
    }

Latex templates:
########################################################################################################

It is possible to write templates with LaTex documents.
To do so, first make sure you have specified the template flavour in the config file

.. code-block:: json

    {
        "template": "main.tex",
        "template_flavour_syntax": "latex",
        "conf":
        {
            "title": "Pretty printed relevant information",
            ...


Next write your templates using the following conventions:

* Blocks:  ``\BLOCK{block block_name}\BLOCK{endblock}``
* Line statement:  ``%- line instruction``
* Variables:  ``\VAR{variable_name}``
* Comments (long form):  ``\#{This is a long-form Jinja comment}``
* Comments (short form):  ``%# This is a short-form Jinja comment``


An example ``jinja-test.tex`` is available below:

.. code-block:: latex

    \documentclass{article}
    \begin{document}
    \section{Example}
    An example document using \LaTeX, Python, and Jinja.

    % This is a regular LaTeX comment
    \section{\VAR{section1}}
    \#{This is a long-form Jinja comment}
    \begin{itemize}
    \BLOCK{ for x in range(0, 3) }
      \item Counting: \VAR{x}
    \BLOCK{ endfor }
    \end{itemize}

    \section{\VAR{section2}}
    %# This is a short-form Jinja comment
    \begin{itemize}
    %- for x in range(0, 3)
      \item Counting: \VAR{x}
    %- endfor
    \end{itemize}

    \end{document}


Capabilities
====================================================

eds4jinja2 turns a Jinja2 template into a self-describing report: the template declares *how* to
fetch its data and the environment resolves it at render time. The available capabilities are:

* **File data sources** (``from_file``) - tabular and tree-structured files.
* **Remote SPARQL** (``from_endpoint``) - query a live SPARQL endpoint (tabular or tree).
* **In-memory graph data sources** (``from_graph`` / ``from_rdf``) - render against an in-process
  RDF graph with no SPARQL server (see below).
* **Parallel report execution** - optionally pre-fetch all queries concurrently before rendering
  (see below).
* **Template flavours** - HTML/XML and LaTeX syntax (see `Latex templates:`_).
* **Builder injection** - override or add data-source builders/filters per ``ReportBuilder``.

In-memory graph data sources
####################################################

Two builders render reports against an in-process RDF graph - no Fuseki/SPARQL server required.

Query a graph you already hold (an ``rdflib.Graph``, a ``pyoxigraph`` store, or any
``query(sparql)`` callable):

.. code-block:: jinja

    {% set rows, error = from_graph(my_graph).with_query("SELECT ?s WHERE { ?s a ex:Thing }").fetch_tabular() %}

Load RDF file(s)/URL(s) into an in-memory graph (engine ``rdflib`` by default, or ``oxigraph``)
and query it - both ``fetch_tabular`` and ``fetch_tree`` are supported:

.. code-block:: jinja

    {% set rows, error = from_rdf(["data.ttl", "http://example.org/more.ttl"], "oxigraph").with_query(q).fetch_tabular() %}

To render an **existing** report against an in-memory graph with the **templates unchanged**,
inject a builder that overrides ``from_endpoint`` (which the templates already call):

.. code-block:: py3

    import rdflib
    from eds4jinja2 import InMemorySPARQLDataSource
    from eds4jinja2.services.report_builder import ReportBuilder

    graph = rdflib.Graph().parse("dataset.ttl")  # the consumer owns loading / manipulation
    ReportBuilder(
        "report/",
        external_data_source_builders={"from_endpoint": lambda _endpoint: InMemorySPARQLDataSource(graph)},
    ).make_document()

The ``oxigraph`` engine is an optional extra: ``pip install eds4jinja2[oxigraph]``. The ``rdflib``
engine needs no extra dependency.

Parallel report execution
####################################################

For large reports whose runtime is dominated by SPARQL query latency, set ``parallelism`` in the
report ``config.json`` to pre-fetch all data concurrently before rendering:

.. code-block:: json

    { "template": "report.html", "conf": {}, "parallelism": 16 }

Execution is threads-only and **all-or-nothing** (any fetch failure aborts the report, no partial
output); results are staged in a temp folder that is cleaned up afterwards. With ``parallelism``
unset or ``1`` the behaviour is exactly the previous sequential render. Threaded speed-up is real
for remote endpoints and ``oxigraph`` in-memory graphs (both release the GIL); ``rdflib`` in-memory
queries are GIL-bound (correct, limited speed-up).

Development
====================================================

The package follows Cosmic-Python layers, enforced by import-linter:

.. code-block:: text

    entrypoints  ->  services  ->  adapters  ->  models
                                       \------------^
    models       pure domain (no I/O): sparql, data_source (+ Engine), transformations, collections
    adapters     I/O + integration: file/remote/local/in-memory SPARQL, graph_store, query_files, ...
    services     use-case orchestration: jinja_builder, report_builder, parallel_executor, actions
    entrypoints  the `mkreport` CLI

``models`` imports nothing upward; ``adapters`` import only ``models``; ``services`` import
``adapters`` + ``models``; ``entrypoints`` import ``services``.

Tooling is pip + tox + ``pyproject.toml`` (setuptools; not Poetry). The ``make`` targets are the
dev/CI interface:

.. code-block:: bash

    make install-all          # install the project with the dev extra
    make test-unit            # unit tests (tox: py311, py312)
    make test-features        # BDD feature tests
    make test-all             # full suite (excludes live-network tests)
    make check-architecture   # validate the layer boundaries (import-linter)
    make build                # build the wheel/sdist

Tests live under ``tests/unit/`` (isomorphic to the layers: ``models/adapters/services/meta``) and
``tests/steps`` + ``tests/features`` (BDD). The package version is a single source of truth in the
``eds4jinja2/VERSION`` file (read by the package, ``pyproject.toml`` and the docs).

Extending eds4jinja2
====================================================

**Add a new data source.** Subclass ``DataSource`` in the ``adapters`` layer and implement the four
abstract methods; the base class wraps them in fail-safe ``fetch_tabular`` / ``fetch_tree``
(returning ``(content, error)``).

.. code-block:: py3

    # eds4jinja2/adapters/my_source.py
    from eds4jinja2.models.data_source import DataSource

    class MyDataSource(DataSource):
        def _can_be_tabular(self): return True
        def _can_be_tree(self): return False
        def _fetch_tabular(self): ...   # return a pandas DataFrame
        def _fetch_tree(self): ...      # return a dict / raise UnsupportedRepresentation

Register it as a template builder in ``services/jinja_builder.py``:

.. code-block:: py3

    DATA_SOURCE_BUILDERS = {
        ...,
        "from_my_source": lambda location: MyDataSource(location),
    }

Templates can then call ``{{ from_my_source(...).fetch_tabular() }}``. Alternatively, inject the
builder per report without editing the library, via
``ReportBuilder(..., external_data_source_builders={"from_my_source": ...})``.

**Respect the layers.** Pure domain logic goes in ``models`` (no I/O), integration in ``adapters``,
orchestration in ``services``. Run ``make check-architecture`` - the import-linter contracts fail
the build if a boundary is crossed (e.g. a model importing an adapter).

**Add an in-memory engine.** The built-in graph store (``adapters/graph_store.py``) exposes a
``GraphStorePort``; add a new ``...GraphStore`` implementation and wire it into ``make_graph_store``
behind a new ``Engine`` value. Reuse ``InMemorySPARQLDataSource`` for tabular/tree parity.

Indices and tables
===================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
