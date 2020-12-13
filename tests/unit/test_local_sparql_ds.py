"""
test_sparql_ds.py
Date:  25/09/2020
Author: Laurentiu Mandru
Email: mclaurentiu79@gmail.com
"""
import os
import pathlib
import pytest
from eds4jinja2 import RDFFileDataSource

from eds4jinja2.adapters.base_data_source import UnsupportedRepresentation


def test_load_local_sparql_fetch_tabular():
    local_rdf_ds = RDFFileDataSource(
        str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))

    local_rdf_ds.with_query("""SELECT *
            WHERE {
                 ?s ?p ?o
            }
            limit 10""")
    local_rdf_ds.fetch_tabular()


def test_load_local_sparql_substitution():
    local_rdf_ds = RDFFileDataSource(
        str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))

    local_rdf_ds.with_query("""SELECT *
            WHERE {
                 ~a ~b ~c
            }
            limit 10""", {'a': '?s', 'b': '?p', 'c': '?o'})
    assert local_rdf_ds.__query__ == """SELECT *
            WHERE {
                 ?s ?p ?o
            }
            limit 10"""


def test_load_local_query_from_file_sparql_fetch_tabular():
    local_rdf_ds = RDFFileDataSource(
        str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))

    local_rdf_ds.with_query_from_file(pathlib.Path("./tests/test_data/queries/spo_limit_10.txt"))
    local_rdf_ds.fetch_tabular()


def test_load_local_query_from_file_substitution():
    local_rdf_ds = RDFFileDataSource(
        str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))

    local_rdf_ds.with_query_from_file(pathlib.Path("./tests/test_data/queries/spo_limit_10.txt"),
                                      {'substitution_placeholder': 'after_substitution'})
    assert 'after_substitution' in local_rdf_ds.__query__
    assert '~substitution_placeholder' not in local_rdf_ds.__query__


def test_load_local_query_from_file_and_direct_text_sparql_fetch_tabular():
    local_rdf_ds = RDFFileDataSource(
        str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))

    local_rdf_ds.with_query_from_file(pathlib.Path("./tests/test_data/queries/spo_limit_10.txt"))
    with pytest.raises(Exception):
        local_rdf_ds.with_query("""SELECT *
                WHERE {
                     ?s ?p ?o
                }
                limit 10""")
    local_rdf_ds.fetch_tabular()


def test_load_local_sparql_fetch_tree():
    with pytest.raises(UnsupportedRepresentation):
        local_rdf_ds = RDFFileDataSource(
            str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))
        local_rdf_ds.with_query("""SELECT *
                WHERE {
                     ?s ?p ?o
                }
                limit 10""")
        local_rdf_ds._fetch_tree()


def test_load_local_sparql_fetch_tabular_inexistent_file():
    local_rdf_ds = RDFFileDataSource(
        str(pathlib.Path("inexistent.ttl")))

    local_rdf_ds.with_query("""SELECT *
            WHERE {
                 ?s ?p ?o
            }
            limit 10""")
    result = local_rdf_ds.fetch_tabular()
    assert "[Errno 2] No such file or directory" in str(result)
