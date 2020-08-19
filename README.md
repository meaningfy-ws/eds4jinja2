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

# Documentation

[Read the docs here](https://eds4jinja2.readthedocs.io/en/latest/)  
