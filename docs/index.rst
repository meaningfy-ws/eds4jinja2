.. eds4jinja2 documentation master file


Embedded Datasource Specification in Jinja2 templates (v. |release|)
============================================================================

.. toctree::
    :maxdepth: 2

An easy way to reports generation with Jinja2 templates. With Embedded Datasource Specifications inside Jinja2 templates, you can fetch the data you need on the spot.

You can specify the file data source in your JINJA templates as follows. The *path* can be specified as absolute or
relative to the running script.

.. code-block:: Jinja

    {% set content, error = from_file(path).fetch_tree() %} \n
    content:  {{ content }}\n
    error: {{ error }}\n

In case you need to fetch data from a SPARQL endpoint, define a sparql_endpoint (usually in the global configuration)
and a custom sparql query_text. Use them in the template like this:

.. code-block:: Jinja
    {% set query_string = "select * where {?s ?p ?o} limit 10" %}
    {% set content, error =
        from_endpoint(endpoint).with_query(query_string).fetch_tabular() %}
    content:  {{ content }} \n
    error: {{ error }} \n

Currently supported data sources are:

* from file - tabular (CSV, Excel, etc.) and tree-structured (JSON, YAML, etc.)
* from SPARQL endpoint - through a select query or describe request

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


What you would normally do is retreive first all the data and then pass it to the rendered template.

Alternatively, with **eds4jinja2** you can simply specify how the data shall be retreived and then
just use it in the tempalte.

1. instantiate the template from eds4jinaj2 environment

.. code-block:: py3

    from eds4jinja2.builders.jinja_builder import build_eds_environment
    from jinja2 import PackageLoader

    loader=PackageLoader('your_application', 'templates')
    env = build_eds_environment(loader=loader)


2. create a template file 'mytemplate.txt' that looks like this

.. code-block:: jinja

    {% set config_content, error = from_file("path/to/the/config/file.json").fetch_tree() %}\n
    The configuration content: \n
    {{ config_content }} \n

    {% set query_string = "select * where {?s ?p ?o} limit 10" %}
    {% set endpoint_content, error = from_endpoint(endpoint).with_query(query_string).fetch_tree() %} \n
    content: {{ endpoint_content }}\n
    error: {{ error }}\n

3. render the template with no context. The context is dynamically generated during the template rendering. Bingo!

.. code-block:: py3

    rendered_text = template.render()


So, what are the benefits?
####################################################

* your python code is agnostic of what data the template displays
* data fetching functionality is no longer part of the python context-building logic
* the queries and the template to visualise the query result set are tightly coupled and easy to modify
* this allows for building quickly custom visualisation templates (or modifying existent ones), before you even decide what the final query looks like


Indices and tables
===================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
