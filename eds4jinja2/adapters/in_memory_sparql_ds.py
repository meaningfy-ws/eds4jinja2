#!/usr/bin/python3

# in_memory_sparql_ds.py
# An engine-agnostic, in-process SPARQL data source.

"""
A data source that queries an in-memory RDF graph held by the consumer — no SPARQL server and no
file I/O. It accepts either an ``rdflib.Graph`` or a ``query(sparql_text)`` callable (e.g. a
pyoxigraph store's ``query`` method), so it serves rdflib and pyoxigraph consumers alike *without*
eds4jinja2 importing pyoxigraph.

Result shapes mirror :class:`RemoteSPARQLEndpointDataSource` exactly so templates cannot tell which
source produced the data: tabular -> a pandas ``DataFrame`` of stringified bindings; tree -> the
SPARQL-1.1 JSON results dict (built from the :class:`SparqlResults` model), closing the tree gap
that ``RDFFileDataSource`` leaves open.
"""
import pandas as pd
import rdflib

from eds4jinja2.adapters.base_data_source import DataSource
from eds4jinja2.adapters.sparql_query import build_query, read_query_file, is_empty_query, EMPTY_QUERY_ERROR
from eds4jinja2.adapters.sparql_results import SparqlResults, SparqlTerm
# Re-exported for callers that import the SPARQL-JSON keys from this module.
from eds4jinja2.adapters.sparql_results import (  # noqa: F401
    HEAD, VARS, RESULTS, BINDINGS, TYPE, VALUE, DATATYPE, XML_LANG, URI, LITERAL, BNODE,
)


class InMemorySPARQLDataSource(DataSource):
    """
        Query an in-process RDF graph by SPARQL.

        >>> ds = InMemorySPARQLDataSource(rdflib_graph)
        >>> df, error = ds.with_query("SELECT * WHERE {?s ?p ?o}").fetch_tabular()

        A pyoxigraph (or any) backend is supported via a query callable:

        >>> ds = InMemorySPARQLDataSource(store.query)
        >>> tree, error = ds.with_query(sparql).fetch_tree()
    """

    def __init__(self, source):
        if isinstance(source, rdflib.Graph):
            self.__query_fn = source.query
        elif callable(source):
            self.__query_fn = source
        else:
            raise TypeError(
                "source must be an rdflib.Graph or a query(sparql_text) callable, "
                f"got {type(source).__name__}")
        self.__query = ""
        self.__can_be_tabular = True
        self.__can_be_tree = True

    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   prefixes: str = "") -> 'InMemorySPARQLDataSource':
        self.__query = build_query(sparql_query, substitution_variables, prefixes)
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'InMemorySPARQLDataSource':
        self.__query = build_query(read_query_file(sparql_query_file_path), substitution_variables, prefixes)
        return self

    def _assert_query(self):
        if is_empty_query(self.__query):
            raise Exception(EMPTY_QUERY_ERROR)

    def _fetch_tabular(self):
        self._assert_query()
        rows = [{var: str(term) for var, term in binding.items()}
                for binding in _iter_bindings(self.__query_fn(self.__query))]
        return pd.DataFrame(rows)

    def _fetch_tree(self):
        self._assert_query()
        return _to_results(self.__query_fn(self.__query)).to_sparql_json()

    def _can_be_tree(self) -> bool:
        return self.__can_be_tree

    def _can_be_tabular(self) -> bool:
        return self.__can_be_tabular

    def __str__(self):
        return f"from <in-memory graph> {str(self.__query)[:60]} ..."


# --- engine-agnostic normalisation (rdflib Result OR pyoxigraph-shaped solutions) -------------

def _variables(result) -> list:
    if hasattr(result, "vars"):  # rdflib.query.Result
        return [str(variable) for variable in (result.vars or [])]
    return [str(variable).lstrip("?") for variable in getattr(result, "variables", [])]


def _iter_bindings(result):
    """ Yield each solution as a {variable_name: term} mapping, engine-agnostically. """
    if hasattr(result, "bindings"):  # rdflib.query.Result
        for binding in result.bindings:
            yield {str(variable): term for variable, term in binding.items()}
        return
    variables = _variables(result)  # pyoxigraph-style QuerySolutions
    for solution in result:
        row = {}
        for variable in variables:
            try:
                term = solution[variable]
            except (KeyError, IndexError):
                term = None
            if term is not None:
                row[variable] = term
        yield row


def _to_results(result) -> SparqlResults:
    return SparqlResults(
        variables=_variables(result),
        bindings=[{var: _term_to_model(term) for var, term in binding.items()}
                  for binding in _iter_bindings(result)])


def _term_to_model(term) -> SparqlTerm:
    model = _rdflib_term(term)
    return model if model is not None else _foreign_term(term)


def _rdflib_term(term):
    """ SparqlTerm for an rdflib term, or None if it is not an rdflib term. """
    if isinstance(term, rdflib.URIRef):
        return SparqlTerm.uri(str(term))
    if isinstance(term, rdflib.BNode):
        return SparqlTerm.bnode(str(term))
    if isinstance(term, rdflib.Literal):
        if term.language:
            return SparqlTerm.literal(str(term), language=term.language)
        datatype = str(term.datatype) if term.datatype is not None else None
        return SparqlTerm.literal(str(term), datatype=datatype)
    return None


def _foreign_term(term) -> SparqlTerm:
    """ SparqlTerm for a pyoxigraph (or other) term, classified by class name without import. """
    class_name = type(term).__name__
    if class_name == "NamedNode":
        return SparqlTerm.uri(term.value)
    if class_name == "BlankNode":
        return SparqlTerm.bnode(term.value)
    if class_name == "Literal":
        language = getattr(term, "language", None)
        if language:
            return SparqlTerm.literal(term.value, language=language)
        datatype = getattr(term, "datatype", None)
        datatype_value = getattr(datatype, "value", str(datatype)) if datatype is not None else None
        return SparqlTerm.literal(term.value, datatype=datatype_value)
    return SparqlTerm.literal(str(term))
