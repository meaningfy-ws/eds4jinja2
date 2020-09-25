"""
test_sparql_ds.py
Date:  25/09/2020
Author: Laurentiu Mandru
Email: mclaurentiu79@gmail.com
"""
import pathlib
import pytest
from eds4jinja2 import LocalSPARQLDataSource


from eds4jinja2.adapters.base_data_source import UnsupportedRepresentation


def test_load_local_sparql_fetch_tabular():
    local_rdf_ds = LocalSPARQLDataSource(
        str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))

    local_rdf_ds.with_query("""SELECT *
            WHERE {
                 ?s ?p ?o
            }
            limit 10""")
    local_rdf_ds.fetch_tabular()


def test_load_local_sparql_fetch_tree():
    with pytest.raises(UnsupportedRepresentation):
        local_rdf_ds = LocalSPARQLDataSource(
            str(pathlib.Path("../test_data/shacl.example.shapes.ttl")))
        local_rdf_ds.with_query("""SELECT *
                WHERE {
                     ?s ?p ?o
                }
                limit 10""")
        local_rdf_ds._fetch_tree()


def test_load_local_sparql_fetch_tabular_inexistent_file():
    local_rdf_ds = LocalSPARQLDataSource(
        str(pathlib.Path("inexistent.ttl")))

    local_rdf_ds.with_query("""SELECT *
            WHERE {
                 ?s ?p ?o
            }
            limit 10""")
    result = local_rdf_ds.fetch_tabular()
    assert "[Errno 2] No such file or directory" in str(result)
