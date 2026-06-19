#!/usr/bin/python3

# sparql_results.py
# Typed model of the SPARQL 1.1 Query Results JSON shape — the single home for its keys.

"""
The SPARQL-1.1 Query Results JSON structure, modelled with Pydantic so its key names live in one
place and are not duplicated as free strings across adapters. Use the model internally; serialise
to the canonical dict at the boundary (templates and the remote source both speak that dict, so
parity is preserved).
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

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
