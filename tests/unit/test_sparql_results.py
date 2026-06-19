"""
test_sparql_results.py

Unit tests for the SPARQL-results Pydantic model and its serialisation to the canonical
SPARQL-1.1 Query Results JSON dict (the shape templates and the remote source rely on).
"""
from eds4jinja2.adapters.sparql_results import (
    SparqlTerm, SparqlResults, HEAD, VARS, RESULTS, BINDINGS, TYPE, VALUE, DATATYPE, XML_LANG,
    URI, LITERAL, BNODE,
)


def test_term_uri():
    assert SparqlTerm.uri("http://e/a").to_json() == {TYPE: URI, VALUE: "http://e/a"}


def test_term_bnode():
    assert SparqlTerm.bnode("b0").to_json() == {TYPE: BNODE, VALUE: "b0"}


def test_term_literal_plain_excludes_none():
    assert SparqlTerm.literal("hi").to_json() == {TYPE: LITERAL, VALUE: "hi"}


def test_term_literal_with_language_uses_alias():
    assert SparqlTerm.literal("hi", language="en").to_json() == {
        TYPE: LITERAL, VALUE: "hi", XML_LANG: "en"}


def test_term_literal_with_datatype():
    out = SparqlTerm.literal("5", datatype="http://www.w3.org/2001/XMLSchema#int").to_json()
    assert out == {TYPE: LITERAL, VALUE: "5", DATATYPE: "http://www.w3.org/2001/XMLSchema#int"}


def test_empty_results_canonical_shape():
    assert SparqlResults.empty().to_sparql_json() == {
        HEAD: {VARS: []}, RESULTS: {BINDINGS: []}}


def test_results_to_sparql_json():
    results = SparqlResults(
        variables=["s", "o"],
        bindings=[{"s": SparqlTerm.uri("http://e/a"), "o": SparqlTerm.literal("hi", language="en")}])
    tree = results.to_sparql_json()
    assert tree[HEAD][VARS] == ["s", "o"]
    assert tree[RESULTS][BINDINGS][0]["s"] == {TYPE: URI, VALUE: "http://e/a"}
    assert tree[RESULTS][BINDINGS][0]["o"] == {TYPE: LITERAL, VALUE: "hi", XML_LANG: "en"}
