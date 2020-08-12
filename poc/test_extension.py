"""
test_extension.py
Date:  06/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
import json

from jinja2 import Template, contextfunction, Environment
from jinja2.ext import Extension
from jinja2.runtime import Context
from SPARQLWrapper import SPARQLWrapper, JSON, CSV
import pandas as pd


@contextfunction
def example_function(context):
    context['z'] = "1243453"
    return "example function"


class SpecialContextObject(dict):
    def call_something(self, param):
        return "string plus an extra " + str(param)

    def fet_local_json_file(self, file_name):
        """
            return the json object loaded from a local file
        :param file_name:
        :return:
        """

    def query_json(self, queryString):
        endpoint = SPARQLWrapper("http://publications.europa.eu/webapi/rdf/sparql")
        endpoint.setQuery(queryString)
        endpoint.setReturnFormat(JSON)
        return endpoint.query().convert()

    def query_pd(self, queryString):
        endpoint = SPARQLWrapper("http://publications.europa.eu/webapi/rdf/sparql")
        endpoint.setQuery(queryString)
        endpoint.setReturnFormat(CSV)
        tabular = endpoint.queryAndConvert()
        return pd.read_csv(pd.compat.StringIO(str(tabular, "utf-8")))


class EDSEnvironment(Environment):
    def __init__(self, **kwargs):
        super(EDSEnvironment, self).__init__(**kwargs)
        self.globals['static'] = "this is a static file"
        self.globals['reverse'] = "this is a special object"


# Template.environment_class = EDSEnvironment
# Environment.template_class = SpecialTemplate


template = '''
{% set queryString = 'SELECT * WHERE { ?s ?p ?o. } limit 10' %}\n
{% set q = x.query_json(queryString) %} \n
query {{ q }}\n
'''

values = SpecialContextObject()
values['a'] = "aaaa"
values['b'] = "bbb"

t = Template(template)
print(t.render(x=values))

# -------------------------------------------------------------
print("-" * 40)
# -------------------------------------------------------------

template = '''
{% set queryString = 'SELECT * WHERE { ?s ?p ?o. } limit 10' %}\n
{% set q = x.query_json(queryString) %} \n
query {{ q }}\n
context available {{ static }} and {{ reverse }}\n
funct {{ f1('dfhgf') }} \n
'''

env = Environment()
env.globals['static'] = "this is a static file"
env.globals['reverse'] = "this is a special object"
env.globals['f1'] = lambda x: f"Hello {x}!"

tt = env.from_string(template)
print(tt.render(x=values))