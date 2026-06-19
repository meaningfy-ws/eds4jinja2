"""
test_in_memory_builders.py

Tests for the in-memory data-source builders registered in DATA_SOURCE_BUILDERS:
`from_graph` (alias `from_memory`).
"""
import rdflib

from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource
from eds4jinja2.services.jinja_builder import DATA_SOURCE_BUILDERS


def test_from_graph_registered_and_builds_in_memory_source():
    assert "from_graph" in DATA_SOURCE_BUILDERS
    ds = DATA_SOURCE_BUILDERS["from_graph"](rdflib.Graph())
    assert isinstance(ds, InMemorySPARQLDataSource)


def test_from_memory_alias_registered():
    assert "from_memory" in DATA_SOURCE_BUILDERS
    ds = DATA_SOURCE_BUILDERS["from_memory"](rdflib.Graph())
    assert isinstance(ds, InMemorySPARQLDataSource)
