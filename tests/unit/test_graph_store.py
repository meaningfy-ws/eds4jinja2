"""
test_graph_store.py

Unit tests for the built-in graph store: load RDF file(s) into an in-memory graph
(rdflib by default, oxigraph opt-in) once, and query it.
"""
import importlib.util

import pytest
import rdflib

from eds4jinja2.adapters.graph_store import (
    Engine, RdflibGraphStore, GraphStorePort, make_graph_store, OXIGRAPH_MISSING_MESSAGE,
    _is_url, _media_type_for, _as_source_list, DEFAULT_RDF_FORMAT,
)
from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource

OXIGRAPH_INSTALLED = importlib.util.find_spec("pyoxigraph") is not None

TTL = """
@prefix ex: <http://example.org/> .
ex:a a ex:Thing ; ex:label "alpha" .
ex:b a ex:Thing ; ex:label "beta" .
"""
SELECT_THINGS = "PREFIX ex: <http://example.org/> SELECT ?s WHERE { ?s a ex:Thing }"


@pytest.fixture
def ttl_file(tmp_path):
    path = tmp_path / "data.ttl"
    path.write_text(TTL)
    return path


def test_engine_enum_values_and_rejects_unknown():
    assert Engine("rdflib") is Engine.RDFLIB
    assert Engine("oxigraph") is Engine.OXIGRAPH
    with pytest.raises(ValueError):
        Engine("bogus")


def test_rdflib_store_loads_and_queries(ttl_file):
    store = make_graph_store(Engine.RDFLIB, sources=[ttl_file])
    assert isinstance(store, GraphStorePort)
    result = store.query(SELECT_THINGS)
    assert len(list(result)) == 2


def test_make_graph_store_default_engine_is_rdflib(ttl_file):
    store = make_graph_store(sources=ttl_file)  # single source, default engine
    assert isinstance(store, RdflibGraphStore)


def test_sources_loaded_once_at_construction(ttl_file):
    # The graph is populated at construction, not lazily per query (no re-parse smell).
    store = make_graph_store(Engine.RDFLIB, sources=[ttl_file])
    assert len(store.graph) > 0  # already loaded before any query


def test_multiple_sources_merge_into_one_graph(tmp_path):
    a = tmp_path / "a.ttl"
    a.write_text("@prefix ex: <http://example.org/> . ex:a a ex:Thing .")
    b = tmp_path / "b.ttl"
    b.write_text("@prefix ex: <http://example.org/> . ex:b a ex:Thing .")
    store = make_graph_store(Engine.RDFLIB, sources=[a, b])
    assert len(list(store.query(SELECT_THINGS))) == 2


def test_from_rdf_via_in_memory_source_tabular_and_tree(ttl_file):
    # The builder composition: from_rdf -> store -> InMemorySPARQLDataSource
    store = make_graph_store(Engine.RDFLIB, sources=[ttl_file])
    ds = InMemorySPARQLDataSource(store.query).with_query(SELECT_THINGS)
    df, error = ds.fetch_tabular()
    assert error is None and len(df) == 2
    tree, error = ds.fetch_tree()
    assert error is None and len(tree["results"]["bindings"]) == 2


def test_source_helpers():
    assert _is_url("http://x/y") and _is_url("https://x")
    assert not _is_url("/local/path.ttl")
    assert _media_type_for("a.ttl") == "text/turtle"
    assert _media_type_for("a.rdf") == "application/rdf+xml"
    assert _media_type_for("a.unknown") == DEFAULT_RDF_FORMAT
    assert _as_source_list(None) == []
    assert _as_source_list("a.ttl") == ["a.ttl"]
    assert _as_source_list(["a.ttl", "b.ttl"]) == ["a.ttl", "b.ttl"]


@pytest.mark.skipif(OXIGRAPH_INSTALLED, reason="pyoxigraph IS installed; testing the missing-dep path")
def test_oxigraph_missing_dependency_message(ttl_file):
    with pytest.raises(ImportError) as exc:
        make_graph_store(Engine.OXIGRAPH, sources=[ttl_file])
    assert OXIGRAPH_MISSING_MESSAGE in str(exc.value)


@pytest.mark.skipif(not OXIGRAPH_INSTALLED, reason="pyoxigraph not installed")
def test_oxigraph_store_loads_and_queries(ttl_file):
    store = make_graph_store(Engine.OXIGRAPH, sources=[ttl_file])
    ds = InMemorySPARQLDataSource(store.query).with_query(SELECT_THINGS)
    df, error = ds.fetch_tabular()
    assert error is None and len(df) == 2
