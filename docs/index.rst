.. eds4jinja2 documentation master file

Embedded Datasource Specification in Jinja2 templates (v. |release|)
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Specify the data sources in your JINJA templates directly.

::

    {% set content, error = from_file(path).fetch_tree() %} \n
    content:  {{ content }}\n
    error: {{ error }}\n

::

    {% set content, error =
        from_endpoint(endpoint).with_query(query_string).fetch_tabular() %}
    content:  {{ content }} \n
    error: {{ error }} \n


Currently supported data sources are:

* from file - tabular (CSV, Excel, etc.) and tree-structured (JSON, YAML, etc.)
* from SPARQL endpoint - through a select query or describe request

Not yet implemented

* from a XML file
* from a REST API
* from a relational database
* from a NoSQL database, e.g. MongoDB
* from a graph database, e.g. TinkerPop, Neo4j


But why?
#####################################
For example, imagine that you need the content of a JSON file in a template.

**In this case, what you would normally do is**


1. instantiate the template from an environment
::
   from jinja2 import Environment, PackageLoader, select_autoescape

   loader=PackageLoader('yourapplication', 'templates')
   env = Environment(loader)
   template = env.get_template('mytemplate.txt')

2. create a template file 'mytemplate.txt' that looks like this
::
    The file content:
    {{ data }}

3. fetch the data content from file (the context building functionality)
::
   content  = json.load("path/to/the/file.json")

4. render the template with a carefully prepared context
::
   rendered_text = template.render(data=content)

**With eds2jinja2 it is much simpler**


1. instantiate the template from eds4jinaj2 environment
::
    from eds4jinja2.builders.jinja_builder import build_eds_environment
    from jinja2 import PackageLoader

    loader=PackageLoader('yourapplication', 'templates')
    env = build_eds_environment(loader=loader)

2. create a template file 'mytemplate.txt' that looks like this
::
    {% set content, error = from_file("path/to/the/file.json").fetch_tree() %}\n
    The file content: \n
    {{ content }} \n

3. render the template with no context. The context is dynamically generated during the template rendering.
::
    rendered_text = template.render()

**To query a SPARQL endpoint**

Repeat the steps from the example above to instantiate the environment and render the template. But adapt teh template as follows.

2. modify the template file 'mytemplate.txt' to looks like this
::
    {% set query_string = "select * where {?s ?p ?o} limit 10" %}
    {% set content, error = from_endpoint(endpoint).with_query(query_string).fetch_tree() %} \n
    content: {{ content }}\n
    error: {{ error }}\n

So, what are the benefits?
####################################################

* your python code is agnostic of what data teh template displays
* data fetching functionality is no longer part of the python context-building logic
* the queries and the template to visualise the query result set are tightly coupled and easy to modify
* this allows for building quickly custom visualisation templates (or modifying existent ones), before you even decide what the final query looks like


Indices and tables
===================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
