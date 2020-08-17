"""
test_sparql_ds.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from urllib.error import URLError

import pytest
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, URITooLong

from eds4jinja2.adapters.sparql_ds import SPARQLEndpointDataSource
from tests import ENDPOINT_REMOTE_CORRECT, DUMMY_DESCRIBE_URI, SPO_LIMIT_10, WRONG_SPO_LIMIT_10, \
    QUERY_LONGER_THAN_2048KB, ENDPOINT_INEXISTENT_SERVER, DUMMY_DESCRIBE_URI_GRAPH


def test_connect_to_remote_endpoint():
    fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
    response_text = str(fds.with_uri(DUMMY_DESCRIBE_URI)._fetch_tree())
    assert len(response_text) > 2000
    assert "results" in response_text


def test_connect_to_endpoint_fails():
    with pytest.raises(ValueError):
        fds = SPARQLEndpointDataSource("")
        fds._fetch_tree()

    with pytest.raises(URLError):
        fds = SPARQLEndpointDataSource(ENDPOINT_INEXISTENT_SERVER)
        fds._fetch_tree()

    with pytest.raises(QueryBadFormed):
        fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
        fds.with_query(WRONG_SPO_LIMIT_10)._fetch_tree()
        fds._fetch_tree()

    with pytest.raises(URITooLong):
        fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
        fds.with_query(QUERY_LONGER_THAN_2048KB)._fetch_tree()


def test_query_endpoint_and_fetch_tree():
    fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
    response_object, error = fds.with_query(SPO_LIMIT_10).fetch_tree()
    assert len(str(response_object)) > 2000
    assert "results" in str(response_object)
    assert error is None


def test_query_endpoint_and_fetch_tabular():
    fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
    response_object, error = fds.with_query(SPO_LIMIT_10).fetch_tabular()
    assert len(str(response_object)) > 500
    assert "http://" in str(response_object)
    assert error is None


def test_fetch_tabular():
    fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
    response_text = str(fds.with_query(SPO_LIMIT_10)._fetch_tabular())
    assert "http://www.w3.org/1999/02/22-rdf-syntax-ns#" in response_text
    # assert "[10 rows x 3 columns]" in response_text


def test_describe_uri():
    fds = SPARQLEndpointDataSource(ENDPOINT_REMOTE_CORRECT)
    response_text = str(fds.with_uri(DUMMY_DESCRIBE_URI, DUMMY_DESCRIBE_URI_GRAPH)._fetch_tabular())
    assert "110" in response_text

    response_text = str(fds.with_uri(DUMMY_DESCRIBE_URI)._fetch_tabular())
    assert "12" in response_text
    assert "110" not in response_text
