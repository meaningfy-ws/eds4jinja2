#!/usr/bin/python3

# sparql_query.py
# Shared SPARQL query-string building, used by every SPARQL data source (no duplication).

"""
The substitution + prefix + file-reading logic was previously copied into each SPARQL data source
(`remote_sparql_ds`, `local_sparql_ds`, `in_memory_sparql_ds`). It lives here once.
"""
from pathlib import Path

from eds4jinja2.adapters.substitution_template import SubstitutionTemplate

EMPTY_QUERY_ERROR = "The query is empty."


def build_query(sparql_query: str, substitution_variables: dict = None, prefixes: str = "") -> str:
    """ Apply ``~``-substitution and prepend prefixes, returning the final query string. """
    if substitution_variables:
        sparql_query = SubstitutionTemplate(sparql_query).safe_substitute(substitution_variables)
    return (prefixes + " " + sparql_query).strip()


def read_query_file(sparql_query_file_path: str) -> str:
    """ Read a SPARQL query from a file path. """
    with open(Path(sparql_query_file_path).resolve(), "r") as query_file:
        return query_file.read()


def is_empty_query(query: str) -> bool:
    return not query or query.isspace()
