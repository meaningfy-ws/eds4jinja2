#!/usr/bin/python3

# query_files.py
# Reading SPARQL query text from files — the I/O half of query handling (adapter layer).

from pathlib import Path


def read_query_file(sparql_query_file_path: str) -> str:
    """ Read a SPARQL query from a file path. """
    with open(Path(sparql_query_file_path).resolve(), "r") as query_file:
        return query_file.read()
