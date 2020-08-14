"""
__init__.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from typing import Tuple, Optional

import pandas as pd

from eds4jinja2.adapters.base_data_source import UnsupportedRepresentation, DataSource
from eds4jinja2.adapters.file_ds import FileDataSource
from eds4jinja2.adapters.sparql_ds import SPARQLEndpointDataSource
from eds4jinja2.builders.jinja_builder import FROM_ENDPOINT, FROM_FILE

SPO_LIMIT_10 = "select * where {?s ?p ?o} limit 10"
DUMMY_DESCRIBE_URI = "http://publications.europa.eu/resource/authority/corporate-body/SPC"
DUMMY_DESCRIBE_URI_GRAPH = "http://publications.europa.eu/resource/authority/corporate-body"

WRONG_SPO_LIMIT_10 = "select * "
QUERY_LONGER_THAN_2048KB = f"select * {{?s ?p <http://{'abc' * 800805}>}} limit 10"

ENDPOINT_LOCAL_CORRECT = "http://localhost:3030/subdiv/sparql"
ENDPOINT_REMOTE_CORRECT = "http://publications.europa.eu/webapi/rdf/sparql"
ENDPOINT_INEXISTENT_SERVER = "http://inexistent/mocked/server:43534645"
ENDPOINT_CRASHED_SERVER = "http://crashed/mocked/server"

RESPONSE_SPARQL_CSV_CORPORATE_BODY = [["s", "p", "o"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/SPC",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://www.w3.org/2004/02/skos/core#Concept"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/SPC",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://publications.europa.eu/ontology/euvoc#Corporate"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/REPRES_FRA",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://www.w3.org/2004/02/skos/core#Concept"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/REPRES_FRA",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://publications.europa.eu/ontology/euvoc#Corporate"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/ICAO",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://www.w3.org/2004/02/skos/core#Concept"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/ICAO",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://publications.europa.eu/ontology/euvoc#Corporate"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/CMT_MIX_EEC_AND",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://www.w3.org/2004/02/skos/core#Concept"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/CMT_MIX_EEC_AND",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://publications.europa.eu/ontology/euvoc#Corporate"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/DEL_COL_ECU",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://www.w3.org/2004/02/skos/core#Concept"],
                                      [
                                          "http://publications.europa.eu/resource/authority/corporate-body/DEL_COL_ECU",
                                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                                          "http://publications.europa.eu/ontology/euvoc#Corporate"]]

RESPONSE_SPARQL_JSON_CORPORATE_BODY = {"head": {"link": [], "vars": ["s", "p", "o"]},
                                       "results": {"distinct": "false", "ordered": "true", "bindings": [
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/SPC"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://www.w3.org/2004/02/skos/core#Concept"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/SPC"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://publications.europa.eu/ontology/euvoc#Corporate"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/REPRES_FRA"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://www.w3.org/2004/02/skos/core#Concept"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/REPRES_FRA"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://publications.europa.eu/ontology/euvoc#Corporate"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/ICAO"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://www.w3.org/2004/02/skos/core#Concept"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/ICAO"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://publications.europa.eu/ontology/euvoc#Corporate"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/CMT_MIX_EEC_AND"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://www.w3.org/2004/02/skos/core#Concept"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/CMT_MIX_EEC_AND"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://publications.europa.eu/ontology/euvoc#Corporate"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/DEL_COL_ECU"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://www.w3.org/2004/02/skos/core#Concept"}},
                                           {"s": {"type": "uri",
                                                  "value": "http://publications.europa.eu/resource/authority/corporate-body/DEL_COL_ECU"},
                                            "p": {"type": "uri",
                                                  "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                            "o": {"type": "uri",
                                                  "value": "http://publications.europa.eu/ontology/euvoc#Corporate"}}]}}

TEMPLATE_DUMMY = '''
{% set content = 'This is a static content' %} \n
content:  {{ content }} \n
'''

TEMPLATE_SPARQL_FETCH_TABULAR = '''
{% set content, error = from_endpoint(endpoint).with_query(query_string).fetch_tabular() %} \n
content:  {{ content }} \n
error: {{ error }} \n
'''

TEMPLATE_SPARQL_FETCH_TREE = '''
{% set content, error = from_endpoint(endpoint).with_query(query_string).fetch_tree() %} \n
content:  {{ content }}\n
error: {{ error }}\n
'''

TEMPLATE_FILE_FETCH_TREE = '''
{% set content, error = from_file(path).fetch_tree() %} \n
content:  {{ content }}\n
error: {{ error }}\n
'''

TEMPLATE_FILE_FETCH_TABULAR = '''
{% set content, error = from_file(path).fetch_tabular() %} \n
content:  {{ content }}\n
error: {{ error }}\n
'''


# TEMPLATE_FILE_FETCH_TABULAR = '''
# -{% set content, error = from_tabular_file(path).fetch_tabular() %} \n
# -{% set content, error = from_tabular_file(path).fetch_tree() %} \n
# ++{% set content, error = from_file(path).fetch_tree() %} \n
# ++{% set content, error = from_file(path).fetch_tabular() %} \n
# -{% set content, error = from_file(path).fetch(TABULAR) %} \n
# -{% set content, error = from_select_endpoint(query_text, endpoint).fetch_tree() %} \n
# -{% set content, error = from_describe_endpoint(uri, endpoint).fetch_tabular() %} \n
# -{% set content, error = from_select_endpoint(query, endpoint).fetch() %} \n
# -{% set content, error = from_endpoint(endpoint).query(query_text).fetch_tree() %} \n
# -{% set content, error = from_endpoint(endpoint).describe(uri).fetch_tree() %} \n
# ++{% set content, error = from_endpoint(endpoint).with_query(query_text).fetch_tree() %} \n
# ++{% set content, error = from_endpoint(endpoint).with_uri(uri).fetch_tree() %} \n
# +{% set content, error = from_endpoint_with_uri(endpoint,uri).fetch_tree() %} \n
# +{% set content, error = from_endpoint_with_query(endpoint,query).fetch_tree() %} \n
# content:  {{ content }}\n
# error: {{ error }}\n
# '''


class DummyDataSource(DataSource):
    """
        dummy data source returning a constant structure
    """

    def __init__(self, value=None):
        self.value = value

    def _fetch_tree(self) -> Tuple[object, Optional[str]]:
        return {"value": self.value}, None

    def _fetch_tabular(self) -> Tuple[object, Optional[str]]:
        if isinstance(self.value, (str, int)):
            return pd.Dataframe({"values": [self.value]}), None
        elif isinstance(self.value, (list, tuple, set)):
            return pd.Dataframe({"values": list(self.value)}), None
        elif isinstance(self.value, dict):
            return pd.Dataframe(self.value), None
        raise UnsupportedRepresentation(f"Unsupported type {type(self.value)}")

    def _can_be_tree(self) -> bool:
        return True

    def _can_be_tabular(self) -> bool:
        return True


class FakeSPARQLEndpointDataSource(SPARQLEndpointDataSource):

    def with_query(self, sparql_query: str):
        return self

    def with_uri(self, uri: str, graph_uri: Optional[str] = None):
        return self

    def _fetch_tree(self):
        return RESPONSE_SPARQL_JSON_CORPORATE_BODY

    def _fetch_tabular(self):
        return pd.DataFrame(RESPONSE_SPARQL_CSV_CORPORATE_BODY)


class FakeFileDataSource(FileDataSource):

    def _fetch_tree(self):
        return RESPONSE_SPARQL_JSON_CORPORATE_BODY

    def _fetch_tabular(self):
        return pd.DataFrame(RESPONSE_SPARQL_CSV_CORPORATE_BODY)

    def _can_be_tree(self) -> bool:
        return True

    def _can_be_tabular(self) -> bool:
        return True


FAKE_DATA_SOURCE_BUILDERS = {
    FROM_ENDPOINT: lambda endpoint: FakeSPARQLEndpointDataSource(endpoint),
    FROM_FILE: lambda file_path: FakeFileDataSource(file_path),
}
