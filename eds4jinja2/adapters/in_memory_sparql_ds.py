#!/usr/bin/python3

# in_memory_sparql_ds.py
# An engine-agnostic, in-process SPARQL data source.

"""
A data source that queries an in-memory RDF graph held by the consumer — no SPARQL
server and no file I/O. It accepts either an ``rdflib.Graph`` or a ``query(sparql_text)``
callable (e.g. a pyoxigraph-backed store's ``query`` method), so it serves rdflib and
pyoxigraph consumers alike *without* eds4jinja2 importing pyoxigraph.

Result shapes mirror :class:`RemoteSPARQLEndpointDataSource` exactly so that templates
cannot tell which source produced the data:

- tabular -> a pandas ``DataFrame`` of stringified bindings;
- tree    -> the SPARQL 1.1 JSON results object, closing the tree gap that
  ``RDFFileDataSource`` leaves open.
"""
from pathlib import Path

import pandas as pd
import rdflib

from eds4jinja2.adapters.base_data_source import DataSource
from eds4jinja2.adapters.substitution_template import SubstitutionTemplate

# SPARQL 1.1 Query Results JSON structural keys and term types (no free strings).
HEAD = "head"
VARS = "vars"
RESULTS = "results"
BINDINGS = "bindings"
TYPE = "type"
VALUE = "value"
DATATYPE = "datatype"
XML_LANG = "xml:lang"
URI = "uri"
LITERAL = "literal"
BNODE = "bnode"

EMPTY_QUERY_ERROR = "The query is empty."


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
        """ Set the query text and return self for chaining. """
        if substitution_variables:
            sparql_query = SubstitutionTemplate(sparql_query).safe_substitute(substitution_variables)
        self.__query = (prefixes + " " + sparql_query).strip()
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'InMemorySPARQLDataSource':
        """ Read the query text from a file and return self for chaining. """
        with open(Path(sparql_query_file_path).resolve(), 'r') as file:
            query_from_file = file.read()
        if substitution_variables:
            query_from_file = SubstitutionTemplate(query_from_file).safe_substitute(substitution_variables)
        self.__query = (prefixes + " " + query_from_file).strip()
        return self

    def _assert_query(self):
        if not self.__query or self.__query.isspace():
            raise Exception(EMPTY_QUERY_ERROR)

    def _fetch_tabular(self):
        self._assert_query()
        result = self.__query_fn(self.__query)
        rows = [{str(var): str(term) for var, term in binding.items()}
                for binding in _iter_bindings(result)]
        return pd.DataFrame(rows)

    def _fetch_tree(self):
        self._assert_query()
        result = self.__query_fn(self.__query)
        return _to_sparql_json(result)

    def _can_be_tree(self) -> bool:
        return self.__can_be_tree

    def _can_be_tabular(self) -> bool:
        return self.__can_be_tabular

    def __str__(self):
        return f"from <in-memory graph> {str(self.__query)[:60]} ..."


def _iter_bindings(result):
    """ Yield each solution as a {variable_name: term} mapping, engine-agnostically. """
    if hasattr(result, "bindings"):  # rdflib.query.Result
        for binding in result.bindings:
            yield {str(var): term for var, term in binding.items()}
        return
    # pyoxigraph-style QuerySolutions: iterable of QuerySolution indexable by name.
    variables = [str(v).lstrip("?") for v in getattr(result, "variables", [])]
    for solution in result:
        row = {}
        for var in variables:
            try:
                term = solution[var]
            except (KeyError, IndexError):
                term = None
            if term is not None:
                row[var] = term
        yield row


def _to_sparql_json(result) -> dict:
    """ Build the SPARQL 1.1 JSON results object from an rdflib or pyoxigraph result. """
    if hasattr(result, "vars"):  # rdflib.query.Result
        variables = [str(v) for v in (result.vars or [])]
        bindings = [{str(var): _term_to_json(term) for var, term in binding.items()}
                    for binding in result.bindings]
        return {HEAD: {VARS: variables}, RESULTS: {BINDINGS: bindings}}
    variables = [str(v).lstrip("?") for v in getattr(result, "variables", [])]
    bindings = []
    for solution in result:
        row = {}
        for var in variables:
            try:
                term = solution[var]
            except (KeyError, IndexError):
                term = None
            if term is not None:
                row[var] = _term_to_json(term)
        bindings.append(row)
    return {HEAD: {VARS: variables}, RESULTS: {BINDINGS: bindings}}


def _term_to_json(term) -> dict:
    """ Map a single RDF term (rdflib or pyoxigraph) to a SPARQL-JSON term object. """
    entry = _rdflib_term_to_json(term)
    return entry if entry is not None else _foreign_term_to_json(term)


def _rdflib_term_to_json(term):
    """ SPARQL-JSON for an rdflib term, or None if it is not an rdflib term. """
    if isinstance(term, rdflib.URIRef):
        return {TYPE: URI, VALUE: str(term)}
    if isinstance(term, rdflib.BNode):
        return {TYPE: BNODE, VALUE: str(term)}
    if isinstance(term, rdflib.Literal):
        entry = {TYPE: LITERAL, VALUE: str(term)}
        if term.language:
            entry[XML_LANG] = term.language
        elif term.datatype is not None:
            entry[DATATYPE] = str(term.datatype)
        return entry
    return None


def _foreign_term_to_json(term) -> dict:
    """ SPARQL-JSON for a pyoxigraph (or other) term, classified by class name without import. """
    class_name = type(term).__name__
    if class_name == "NamedNode":
        return {TYPE: URI, VALUE: term.value}
    if class_name == "BlankNode":
        return {TYPE: BNODE, VALUE: term.value}
    if class_name == "Literal":
        entry = {TYPE: LITERAL, VALUE: term.value}
        language = getattr(term, "language", None)
        datatype = getattr(term, "datatype", None)
        if language:
            entry[XML_LANG] = language
        elif datatype is not None:
            entry[DATATYPE] = getattr(datatype, "value", str(datatype))
        return entry
    return {TYPE: LITERAL, VALUE: str(term)}
