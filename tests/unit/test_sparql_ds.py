"""
test_sparql_ds.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from urllib.error import URLError

import pytest
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, URITooLong

from eds.adapters.sparql_ds import SPARQLEndpointDataSource
from tests import ENDPOINT_REMOTE_CORRECT, DUMMY_DESCRIBE_URI, SPO_LIMIT_10, WRONG_SPO_LIMIT_10, \
    QUERY_LONGER_THAN_2048KB


def test_connect_to_remote_endpoint():
    fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
    response_text = str(fds.with_uri(DUMMY_DESCRIBE_URI)._fetch_tree())
    assert len(response_text) > 2000
    assert "results" in response_text


def test_connect_to_endpoint_fails():
    with pytest.raises(ValueError):
        fds = SPARQLEndpointDataSource("")
        print(fds._fetch_tree())

    with pytest.raises(URLError):
        fds = SPARQLEndpointDataSource("http://localhost:34543798")
        print(fds._fetch_tree())

    with pytest.raises(QueryBadFormed):
        fds = SPARQLEndpointDataSource("http://localhost:3030/subdiv/sparql")
        print(fds.with_query(WRONG_SPO_LIMIT_10)._fetch_tree())

    with pytest.raises(URITooLong):
        fds = SPARQLEndpointDataSource("http://localhost:3030/subdiv/sparql")
        print(fds.with_query(QUERY_LONGER_THAN_2048KB)._fetch_tree())


def test_query_endpoint():
    fds = SPARQLEndpointDataSource("http://localhost:3030/subdiv/sparql")
    response_object, error = fds.with_query(SPO_LIMIT_10).fetch_tree()
    assert len(str(response_object)) > 2000
    assert "results" in str(response_object)


def test_describe_uri():
    pass


def test_fetch_tabular():
    fds = SPARQLEndpointDataSource("http://localhost:3030/subdiv/sparql")
    response_object, error = fds.with_query(SPO_LIMIT_10).fetch_tabular()
    assert len(str(response_object)) > 2000


def test_fetch_tree():
    pass
