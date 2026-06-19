#!/usr/bin/python3

# sparql.py
# SPARQL domain model: query-string building, the `~` substitution template, and the
# typed SPARQL-1.1 Query Results JSON model. Pure — no I/O, no frameworks beyond pydantic.

"""
Everything SPARQL that is pure domain lives here:

- :class:`SubstitutionTemplate` — the ``~``-delimited template used to parameterise queries;
- :func:`build_query` / :func:`is_empty_query` — query-string assembly (file reading is the
  adapter's concern, see ``adapters/query_files.py``);
- :class:`SparqlTerm` / :class:`SparqlResults` — the result model whose key names live here once
  and which serialises to the canonical SPARQL-1.1 Results JSON dict at the boundary (templates
  and the remote source both speak that dict, so parity is preserved).
"""
from string import Template
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

EMPTY_QUERY_ERROR = "The query is empty."

# SPARQL 1.1 Query Results JSON structural keys and term types (defined ONCE, imported elsewhere).
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


class SubstitutionTemplate(Template):
    """ A ``string.Template`` whose placeholder delimiter is ``~`` (used to parameterise queries). """
    delimiter = '~'


def build_query(sparql_query: str, substitution_variables: dict = None, prefixes: str = "") -> str:
    """ Apply ``~``-substitution and prepend prefixes, returning the final query string. """
    if substitution_variables:
        sparql_query = SubstitutionTemplate(sparql_query).safe_substitute(substitution_variables)
    return (prefixes + " " + sparql_query).strip()


def is_empty_query(query: str) -> bool:
    return not query or query.isspace()


class SparqlTerm(BaseModel):
    """ One bound RDF term: ``{"type", "value"[, "datatype" | "xml:lang"]}``. """
    model_config = ConfigDict(populate_by_name=True)

    type: str
    value: str
    datatype: Optional[str] = None
    language: Optional[str] = Field(default=None, alias=XML_LANG)

    @classmethod
    def uri(cls, value: str) -> "SparqlTerm":
        return cls(type=URI, value=value)

    @classmethod
    def bnode(cls, value: str) -> "SparqlTerm":
        return cls(type=BNODE, value=value)

    @classmethod
    def literal(cls, value: str, datatype: str = None, language: str = None) -> "SparqlTerm":
        return cls(type=LITERAL, value=value, datatype=datatype, language=language)

    def to_json(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class SparqlResults(BaseModel):
    """ The SPARQL-1.1 Query Results JSON object; ``to_sparql_json`` emits the canonical dict. """
    variables: List[str] = Field(default_factory=list)
    bindings: List[Dict[str, SparqlTerm]] = Field(default_factory=list)

    @classmethod
    def empty(cls) -> "SparqlResults":
        return cls()

    def to_sparql_json(self) -> dict:
        return {
            HEAD: {VARS: list(self.variables)},
            RESULTS: {BINDINGS: [{var: term.to_json() for var, term in row.items()}
                                 for row in self.bindings]},
        }
