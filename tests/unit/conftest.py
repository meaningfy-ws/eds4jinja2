"""
conftest.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""

import pandas as pd
import pytest

from eds4jinja2.adapters import invert_dict
from eds4jinja2.builders.jinja_builder import build_eds_environment
from tests import FAKE_DATA_SOURCE_BUILDERS, RESPONSE_SPARQL_CSV_CORPORATE_BODY, RESPONSE_SPARQL_WITH_NUMBERS


@pytest.fixture(scope="function")
def eds_environment():
    return build_eds_environment(external_data_source_builders=FAKE_DATA_SOURCE_BUILDERS)


@pytest.fixture(scope='function')
def dummy_df():
    return pd.DataFrame(RESPONSE_SPARQL_CSV_CORPORATE_BODY[1:], columns=RESPONSE_SPARQL_CSV_CORPORATE_BODY[0])


@pytest.fixture(scope='function')
def dummy_df_numbers():
    return pd.DataFrame(RESPONSE_SPARQL_WITH_NUMBERS[1:], columns=RESPONSE_SPARQL_WITH_NUMBERS[0])


@pytest.fixture
def dummy_prefixes():
    return {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "yago": "http://yago-knowledge.org/resource/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "dbo": "http://dbpedia.org/ontology/",
            "dbp": "http://dbpedia.org/property/",
            "dc": "http://purl.org/dc/elements/1.1/",
            "owl": "http://www.w3.org/2002/07/owl#",
            # "skos": "http://www.w3.org/2004/02/skos/core#",
            "corporate-body": "http://publications.europa.eu/resource/authority/corporate-body/",
            "euvoc": "http://publications.europa.eu/ontology/euvoc#",
            "dcterms": "http://purl.org/dc/terms/",
            "prov": "http://www.w3.org/ns/prov#",
            "sioc": "http://rdfs.org/sioc/ns#",
            "frbr": "http://purl.org/vocab/frbr/core#",
            "xtypes": "http://purl.org/xtypes/",
            "ont": "http://purl.org/net/ns/ontology-annot#",
            "dct": "http://purl.org/dc/terms/",
            }


@pytest.fixture
def dummy_namespaces(dummy_prefixes):
    return invert_dict(dummy_prefixes, True)
