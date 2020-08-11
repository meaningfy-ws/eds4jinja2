"""
__init__.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""

SPO_LIMIT_10 = "select * where {?s ?p ?o} limit 10"
WRONG_SPO_LIMIT_10 = "select * "
QUERY_LONGER_THAN_2048_CHARACTERS = "select * {" * 205
LOCAL_CORRECT = "http://localhost:3030/subl"
REMOTE_CORRECT = "http://publications.europa.eu/webapi/rdf/sparql"
INEXISTENT_SERVER = "http://inexistent/mocked/server"
CRASHED_SERVER = "http://crashed/mocked/server"

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

TEMPLATE_SPARQL_FETCH_TABULAR = '''
{% set content, error = from_select_endpoint(query_string, endpoint).fetch_tabular() %} \n
content:  {{ content }}
error: {{ error }}
'''

TEMPLATE_SPARQL_FETCH_TREE = '''
{% set content, error = from_select_endpoint(query_string, endpoint).fetch_tree() %} \n
content:  {{ content }}
error: {{ error }}
'''

TEMPLATE_FILE_FETCH_TREE = '''
{% set content, error = from_file(path).fetch_tree() %} \n
content:  {{ content }}
error: {{ error }}
'''

TEMPLATE_FILE_FETCH_TABULAR = '''
{% set content, error = from_file(path).fetch_tabular() %} \n
content:  {{ content }}
error: {{ error }}
'''

TEMPLATE_HTTP_FETCH_TREE = '''
{% set content, error = from_http_endpoint(endpoint, parameters).fetch_tree() %} \n
content:  {{ content }}
error: {{ error }}
'''

TEMPLATE_HTTP_FETCH_TABULAR = '''
{% set content, error = from_http_endpoint(endpoint, parameters).fetch_tabular() %} \n
content:  {{ content }}
error: {{ error }}
'''