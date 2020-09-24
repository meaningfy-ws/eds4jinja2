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
from eds4jinja2.adapters.remote_sparql_ds import RemoteSPARQLEndpointDataSource


SPO_LIMIT_10 = "select * where {?s ?p ?o} limit 10"
DUMMY_DESCRIBE_URI = "http://publications.europa.eu/resource/authority/corporate-body/SPC"
DUMMY_DESCRIBE_URI_GRAPH = "http://publications.europa.eu/resource/authority/corporate-body"

WRONG_SPO_LIMIT_10 = "select * "
QUERY_LONGER_THAN_2048KB = f"select * {{?s ?p <http://{'abc' * 800805}>}} limit 10"

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

RESPONSE_SPARQL_WITH_NUMBERS = [
    ["property", "object_type", "property_type", "subject_cnt", "object_cnt", "pattern_cnt", "min", "max", "avg"],
    ["http://lemon-model.net/lemon#context", "http://www.w3.org/2000/01/rdf-schema#Resource", "object", 104, 2, 205, 1,
     2, 1.98536585365854],
    ["http://lemon-model.net/lemon#context", "http://www.w3.org/2000/01/rdf-schema#Resource", "object", 142, 7, 416, 1,
     7, 3.47115384615385],
    ["http://lemon-model.net/lemon#context", "http://www.w3.org/2000/01/rdf-schema#Resource", "object", 2255, 1, 2255,
     1, 1, 1],
    ["http://lemon-model.net/lemon#context", "http://www.w3.org/2000/01/rdf-schema#Resource", "object", 2501, 8, 2876,
     1, 7, 1.42767732962448],
    ["http://lexvo.org/ontology#script", "http://www.w3.org/2000/01/rdf-schema#Resource", "object", 398, 2, 398, 1, 1,
     1],
    ["http://publications.europa.eu/ontology/euvoc#countryCode", "http://www.w3.org/2000/01/rdf-schema#Resource",
     "object", 2255, 3, 2255, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#localityCode", "http://www.w3.org/2000/01/rdf-schema#Resource",
     "object", 2151, 509, 2151, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#signatureLocation", "http://www.w3.org/2000/01/rdf-schema#Resource",
     "object", 74, 13, 76, 1, 2, 1.05263157894737],
    ["http://publications.europa.eu/ontology/euvoc#status", "http://www.w3.org/2000/01/rdf-schema#Resource", "object",
     104, 3, 104, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#status", "http://www.w3.org/2000/01/rdf-schema#Resource", "object",
     142, 2, 142, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#status", "http://www.w3.org/2000/01/rdf-schema#Resource", "object",
     2255, 2, 2255, 1, 1, 1],
    ["http://www.w3.org/2004/02/skos/core#inScheme", "http://www.w3.org/2002/07/owl#Ontology", "object", 2507, 4, 2507,
     1, 1, 1],
    ["http://www.w3.org/2004/02/skos/core#inScheme", "http://www.w3.org/2002/07/owl#Ontology", "object", 6, 1, 6, 1, 1,
     1],
    ["http://www.w3.org/2004/02/skos/core#inScheme", "http://www.w3.org/2004/02/skos/core#ConceptScheme", "object", 104,
     1, 104, 1, 1, 1],
    ["http://www.w3.org/2004/02/skos/core#inScheme", "http://www.w3.org/2004/02/skos/core#ConceptScheme", "object", 142,
     1, 142, 1, 1, 1],
    ["http://www.w3.org/2004/02/skos/core#inScheme", "http://www.w3.org/2004/02/skos/core#ConceptScheme", "object",
     2255, 1, 2255, 1, 1, 1],
    ["http://www.w3.org/2004/02/skos/core#topConceptOf", "http://www.w3.org/2004/02/skos/core#ConceptScheme", "object",
     2507, 4, 2507, 1, 1, 1],
    ["http://www.w3.org/2004/02/skos/core#topConceptOf", "http://www.w3.org/2004/02/skos/core#ConceptScheme", "object",
     6, 1, 6, 1, 1, 1],
    ["http://www.w3.org/2006/vcard/ns#hasEmail", "http://www.w3.org/2000/01/rdf-schema#Resource", "object", 51, 51, 52,
     1, 2, 1.03846153846154],
    ["http://xmlns.com/foaf/0.1/homepage", "http://www.w3.org/2000/01/rdf-schema#Resource", "object", 45, 44, 45, 1, 1,
     1],
    ["http://data.europa.eu/eli/ontology#date_document", "http://www.w3.org/2001/XMLSchema#date", "data", 83, 30, 83, 1,
     1, 1],
    ["http://data.europa.eu/eli/ontology#first_date_entry_in_force", "http://www.w3.org/2001/XMLSchema#date", "data",
     82, 27, 82, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#endDate", "http://www.w3.org/2001/XMLSchema#date", "data", 1673, 32,
     1673, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#endDate", "http://www.w3.org/2001/XMLSchema#date", "data", 2, 2, 2,
     1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#endDate", "http://www.w3.org/2001/XMLSchema#date", "data", 22, 13,
     22, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#endDate", "http://www.w3.org/2001/XMLSchema#date", "data", 265, 17,
     265, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#endDate", "http://www.w3.org/2001/XMLSchema#date", "data", 289, 32,
     289, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#endDate", "http://www.w3.org/2001/XMLSchema#date", "data", 323, 32,
     323, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#endDate", "http://www.w3.org/2001/XMLSchema#date", "data", 86, 3, 86,
     1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#isTextual", "http://www.w3.org/2001/XMLSchema#boolean", "data", 43,
     2, 43, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#officialJournalDate", "http://www.w3.org/2001/XMLSchema#date",
     "data", 92, 31, 92, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#officialJournalNumber", "http://www.w3.org/2001/XMLSchema#string",
     "data", 92, 32, 92, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#officialJournalSeries", "http://www.w3.org/2001/XMLSchema#string",
     "data", 92, 3, 92, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#order", "http://www.w3.org/2001/XMLSchema#integer", "data", 43, 43,
     43, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 104, 39,
     104, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 142, 70,
     142, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 2255,
     21, 2255, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 2507,
     128, 2507, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 2560,
     128, 2560, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 374, 80,
     374, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 4, 4, 4,
     1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 6, 1, 6,
     1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#startDate", "http://www.w3.org/2001/XMLSchema#date", "data", 7952,
     132, 7952, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#xlChangeNote", "http://publications.europa.eu/ontology/euvoc#XlNote",
     "data", 1, 1, 1, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#xlChangeNote", "http://publications.europa.eu/ontology/euvoc#XlNote",
     "data", 42, 48, 48, 1, 3, 1.33333333333333],
    ["http://publications.europa.eu/ontology/euvoc#xlChangeNote", "http://publications.europa.eu/ontology/euvoc#XlNote",
     "data", 50, 99, 99, 1, 2, 1.98989898989899],
    ["http://publications.europa.eu/ontology/euvoc#xlChangeNote", "http://publications.europa.eu/ontology/euvoc#XlNote",
     "data", 93, 148, 148, 1, 3, 1.77027027027027],
    ["http://publications.europa.eu/ontology/euvoc#xlDefinition", "http://publications.europa.eu/ontology/euvoc#XlNote",
     "data", 142, 142, 142, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#xlDefinition", "http://publications.europa.eu/ontology/euvoc#XlNote",
     "data", 148, 152, 152, 1, 2, 1.05263157894737],
    ["http://publications.europa.eu/ontology/euvoc#xlDefinition", "http://publications.europa.eu/ontology/euvoc#XlNote",
     "data", 6, 10, 10, 1, 2, 1.8],
    ["http://publications.europa.eu/ontology/euvoc#xlHistoryNote",
     "http://publications.europa.eu/ontology/euvoc#XlNote", "data", 1, 1, 1, 1, 1, 1],
    ["http://publications.europa.eu/ontology/euvoc#xlHistoryNote",
     "http://publications.europa.eu/ontology/euvoc#XlNote", "data", 53, 73, 73, 1, 2, 1.54794520547945],
    ["http://purl.org/dc/terms/identifier", "http://www.w3.org/2001/XMLSchema#string", "data", 4, 4, 4, 1, 1, 1],
    ["http://purl.org/dc/terms/relation", "http://www.w3.org/2001/XMLSchema#string", "data", 1589, 753, 1589, 1, 1, 1],
    ["http://purl.org/dc/terms/source", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "data", 152, 22, 152,
     1, 1, 1],
    ["http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString",
     "data", 374, 316, 374, 1, 1, 1],
    ["http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "http://www.w3.org/2001/XMLSchema#string", "data", 3403, 3197,
     3403, 1, 1, 1],
    ["http://www.w3.org/1999/02/22-rdf-syntax-ns#value", "http://www.w3.org/2001/XMLSchema#string", "data", 450, 330,
     450, 1, 1, 1],
    ["http://www.w3.org/2008/05/skos-xl#prefLabel", "http://www.w3.org/2008/05/skos-xl#Label", "data", 2507, 6216, 6216,
     1, 24, 11.4594594594595],
    ["http://www.w3.org/2008/05/skos-xl#prefLabel", "http://www.w3.org/2008/05/skos-xl#Label", "data", 4, 4, 4, 1, 1,
     1],
    ["http://www.w3.org/2008/05/skos-xl#prefLabel", "http://www.w3.org/2008/05/skos-xl#Label", "data", 6, 144, 144, 24,
     24, 24],
]

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


class FakeRemoteSPARQLEndpointDataSource(RemoteSPARQLEndpointDataSource):

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
    "from_endpoint": lambda endpoint: FakeRemoteSPARQLEndpointDataSource(endpoint),
    "from_file": lambda file_path: FakeFileDataSource(file_path),
}
