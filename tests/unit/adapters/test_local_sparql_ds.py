"""
test_local_sparql_ds.py

Tests for RDFFileDataSource (query a local RDF file with SPARQL). Paths are anchored on the
shared `test_data_dir` fixture so the tests actually load the fixture graph regardless of the
working directory, and the tabular fetches assert on the real query result.
"""
import pytest

from eds4jinja2 import RDFFileDataSource
from eds4jinja2.models.data_source import UnsupportedRepresentation

SPO_QUERY = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"


@pytest.fixture
def shapes_ttl(test_data_dir):
    return str(test_data_dir / "shacl.example.shapes.ttl")


@pytest.fixture
def spo_query_file(test_data_dir):
    return str(test_data_dir / "queries" / "spo_limit_10.txt")


def test_load_local_sparql_fetch_tabular(shapes_ttl):
    data_frame, error = RDFFileDataSource(shapes_ttl).with_query(SPO_QUERY).fetch_tabular()
    assert error is None
    assert not data_frame.empty
    assert set(data_frame.columns) == {"s", "p", "o"}
    assert len(data_frame) <= 10


def test_load_local_sparql_fetch_tabular_without_query(shapes_ttl):
    result, error_string = RDFFileDataSource(shapes_ttl).with_query("").fetch_tabular()
    assert result is None
    assert error_string == "The query is empty."


def test_load_local_sparql_substitution(shapes_ttl):
    local_rdf_ds = RDFFileDataSource(shapes_ttl).with_query(
        "SELECT * WHERE { ~a ~b ~c } LIMIT 10", {'a': '?s', 'b': '?p', 'c': '?o'})
    assert local_rdf_ds.__query__ == "SELECT * WHERE { ?s ?p ?o } LIMIT 10"


def test_load_local_query_from_file_sparql_fetch_tabular(shapes_ttl, spo_query_file):
    data_frame, error = RDFFileDataSource(shapes_ttl).with_query_from_file(spo_query_file).fetch_tabular()
    assert error is None
    assert not data_frame.empty
    assert set(data_frame.columns) == {"s", "p", "o"}


def test_load_local_query_from_file_and_prefixes(shapes_ttl, spo_query_file):
    local_rdf_ds = RDFFileDataSource(shapes_ttl).with_query_from_file(spo_query_file, None, "PREFIX TEST")
    assert local_rdf_ds.__query__.startswith("PREFIX TEST")


def test_load_local_query_and_prefixes(shapes_ttl):
    local_rdf_ds = RDFFileDataSource(shapes_ttl).with_query(SPO_QUERY, None, "PREFIX TEST")
    assert local_rdf_ds.__query__.startswith("PREFIX TEST")


def test_load_local_query_from_file_substitution(shapes_ttl, spo_query_file):
    local_rdf_ds = RDFFileDataSource(shapes_ttl).with_query_from_file(
        spo_query_file, {'substitution_placeholder': 'after_substitution'})
    assert 'after_substitution' in local_rdf_ds.__query__
    assert '~substitution_placeholder' not in local_rdf_ds.__query__


def test_setting_query_twice_raises(shapes_ttl, spo_query_file):
    local_rdf_ds = RDFFileDataSource(shapes_ttl).with_query_from_file(spo_query_file)
    with pytest.raises(Exception):
        local_rdf_ds.with_query(SPO_QUERY)
    # the originally-set query still resolves
    data_frame, error = local_rdf_ds.fetch_tabular()
    assert error is None and not data_frame.empty


def test_load_local_sparql_fetch_tree_unsupported(shapes_ttl):
    with pytest.raises(UnsupportedRepresentation):
        RDFFileDataSource(shapes_ttl).with_query(SPO_QUERY)._fetch_tree()


def test_load_local_sparql_fetch_tabular_inexistent_file(test_data_dir):
    local_rdf_ds = RDFFileDataSource(str(test_data_dir / "does_not_exist.ttl")).with_query(SPO_QUERY)
    result, error = local_rdf_ds.fetch_tabular()
    assert result is None
    assert "No such file or directory" in str(error)
