"""
test_sparql_ds.py
Date:  11/08/2020
Author: Laurentiu Mandru
Email: costezki.eugen@gmail.com 
"""
import pathlib

# def reduce_binded_triple_to_string_format(dict_of_binded_variables: dict):
#     return {str(k):str(v) for k,v in dict_of_binded_variables.items()}
import pytest

from eds4jinja2 import LocalSPARQLDataSource


# def reduce_triple_to_string_form(tuple_of_rdflilb_objects: Tuple[object, object, object]):
#     return tuple([str(t) for t in tuple_of_rdflilb_objects])
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


def test_load_local_sparql_fetch_tabular_invalid_file():
    local_rdf_ds = LocalSPARQLDataSource(
        str(pathlib.Path("../test_data/file.binary")))

    local_rdf_ds.with_query("""SELECT *
            WHERE {
                 ?s ?p ?o
            }
            limit 10""")
    result = local_rdf_ds.fetch_tabular()
    assert "invalid start byte" in str(result)
