"""
test_in_memory_sparql_ds.py

Unit tests for InMemorySPARQLDataSource — an engine-agnostic in-process SPARQL
data source that accepts either an rdflib.Graph or a query(sparql_text) callable
and implements both tabular (DataFrame) and tree (SPARQL-JSON) fetching.
"""
import pandas as pd
import pytest
import rdflib

from eds4jinja2.adapters.in_memory_sparql_ds import (
    InMemorySPARQLDataSource, HEAD, VARS, RESULTS, BINDINGS, TYPE, VALUE,
    DATATYPE, XML_LANG, URI, LITERAL, BNODE,
)

TTL = """
@prefix ex: <http://example.org/> .
ex:a a ex:Thing ;
     ex:label "alpha"@en ;
     ex:count 1 ;
     ex:related ex:b ;
     ex:note [ ex:x "blank" ] .
"""

SELECT_ALL = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
SELECT_LABEL = "PREFIX ex: <http://example.org/> SELECT ?l WHERE { ex:a ex:label ?l }"


@pytest.fixture
def graph():
    g = rdflib.Graph()
    g.parse(data=TTL, format="turtle")
    return g


def test_construct_from_graph_fetch_tabular(graph):
    ds = InMemorySPARQLDataSource(graph).with_query(SELECT_ALL)
    df, error = ds.fetch_tabular()
    assert error is None
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["s", "p", "o"]
    assert len(df) == len(graph)  # one row per triple
    # cells are stringified
    assert all(isinstance(v, str) for v in df.iloc[0].tolist())


def test_construct_from_callable_fetch_tabular(graph):
    # a pyoxigraph-style consumer hands in a plain query callable
    ds = InMemorySPARQLDataSource(graph.query).with_query(SELECT_ALL)
    df, error = ds.fetch_tabular()
    assert error is None
    assert list(df.columns) == ["s", "p", "o"]
    assert len(df) == len(graph)


def test_invalid_source_raises_type_error():
    with pytest.raises(TypeError):
        InMemorySPARQLDataSource(42)


def test_empty_query_is_fail_safe(graph):
    df, error = InMemorySPARQLDataSource(graph).fetch_tabular()
    assert df is None
    assert error == "The query is empty."


def test_empty_result_set_returns_empty_dataframe(graph):
    ds = InMemorySPARQLDataSource(graph).with_query(
        "SELECT ?s WHERE { ?s a <http://example.org/Nonexistent> }")
    df, error = ds.fetch_tabular()
    assert error is None
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_substitution_and_prefixes(graph):
    ds = InMemorySPARQLDataSource(graph).with_query(
        "SELECT * WHERE { ~a ~b ~c }",
        substitution_variables={"a": "?s", "b": "?p", "c": "?o"},
        prefixes="PREFIX ex: <http://example.org/>")
    assert ds._InMemorySPARQLDataSource__query.startswith("PREFIX ex:")
    assert "~a" not in ds._InMemorySPARQLDataSource__query
    df, error = ds.fetch_tabular()
    assert error is None and not df.empty


def test_fetch_tree_sparql_json_shape(graph):
    ds = InMemorySPARQLDataSource(graph).with_query(SELECT_LABEL)
    tree, error = ds.fetch_tree()
    assert error is None
    assert set(tree.keys()) == {HEAD, RESULTS}
    assert tree[HEAD][VARS] == ["l"]
    bindings = tree[RESULTS][BINDINGS]
    assert len(bindings) == 1
    entry = bindings[0]["l"]
    assert entry[TYPE] == LITERAL
    assert entry[VALUE] == "alpha"
    assert entry[XML_LANG] == "en"


def test_fetch_tree_term_types(graph):
    ds = InMemorySPARQLDataSource(graph).with_query(SELECT_ALL)
    tree, error = ds.fetch_tree()
    assert error is None
    seen_types = set()
    for binding in tree[RESULTS][BINDINGS]:
        for entry in binding.values():
            seen_types.add(entry[TYPE])
            if entry[TYPE] == LITERAL and entry[VALUE] == "1":
                assert DATATYPE in entry  # xsd:integer carried
    assert URI in seen_types
    assert LITERAL in seen_types
    assert BNODE in seen_types


def test_can_be_flags(graph):
    ds = InMemorySPARQLDataSource(graph)
    assert ds._can_be_tabular() is True
    assert ds._can_be_tree() is True


def test_with_query_from_file(tmp_path, graph):
    query_file = tmp_path / "q.rq"
    query_file.write_text("SELECT ?s ?p ?o WHERE { ~a ~b ~c }")
    ds = InMemorySPARQLDataSource(graph).with_query_from_file(
        str(query_file), substitution_variables={"a": "?s", "b": "?p", "c": "?o"})
    df, error = ds.fetch_tabular()
    assert error is None and not df.empty


# --- engine-agnostic normalisation against pyoxigraph-shaped (duck-typed) results -----------

class _FakeVar:
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return "?" + self._name  # pyoxigraph Variable str form


class _FakeSolution:
    def __init__(self, mapping):
        self._mapping = mapping

    def __getitem__(self, key):
        if key not in self._mapping:
            raise KeyError(key)
        return self._mapping[key]


class _FakeSolutions:
    def __init__(self, variables, rows):
        self.variables = [_FakeVar(v) for v in variables]
        self._rows = rows

    def __iter__(self):
        return iter(self._rows)


class NamedNode:
    def __init__(self, value):
        self.value = value


class BlankNode:
    def __init__(self, value):
        self.value = value


class _FakeDatatype:
    def __init__(self, value):
        self.value = value


class Literal:
    def __init__(self, value, language=None, datatype=None):
        self.value = value
        self.language = language
        self.datatype = _FakeDatatype(datatype) if datatype else None


def _fake_result():
    return _FakeSolutions(
        ["s", "o"],
        [_FakeSolution({"s": NamedNode("http://e/a"), "o": Literal("hi", language="en")}),
         _FakeSolution({"s": BlankNode("b0"), "o": Literal("5", datatype="http://www.w3.org/2001/XMLSchema#int")})])


def test_pyoxigraph_shaped_callable_tabular():
    ds = InMemorySPARQLDataSource(lambda q: _fake_result()).with_query(SELECT_ALL)
    df, error = ds.fetch_tabular()
    assert error is None
    assert list(df.columns) == ["s", "o"]
    assert len(df) == 2


def test_pyoxigraph_shaped_callable_tree_term_types():
    ds = InMemorySPARQLDataSource(lambda q: _fake_result()).with_query(SELECT_ALL)
    tree, error = ds.fetch_tree()
    assert error is None
    assert tree[HEAD][VARS] == ["s", "o"]
    bindings = tree[RESULTS][BINDINGS]
    assert bindings[0]["s"] == {TYPE: URI, VALUE: "http://e/a"}
    assert bindings[0]["o"] == {TYPE: LITERAL, VALUE: "hi", XML_LANG: "en"}
    assert bindings[1]["s"][TYPE] == BNODE
    assert bindings[1]["o"][DATATYPE] == "http://www.w3.org/2001/XMLSchema#int"
