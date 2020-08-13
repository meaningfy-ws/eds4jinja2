# eds4jinja2
Embedded Datasource Specification in Jinja2 templates

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

[Read the docs here](https://eds4jinja2.readthedocs.io/en/feature-mdr-111/)  