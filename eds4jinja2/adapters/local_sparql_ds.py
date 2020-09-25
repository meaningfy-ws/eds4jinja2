#!/usr/bin/python3

# remote_sparql_ds.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com


import pandas as pd
import rdflib

from eds4jinja2.adapters.base_data_source import DataSource, UnsupportedRepresentation

DEFAULT_ENCODING = 'utf-8'


class RDFFileDataSource(DataSource):
    """
        Accesses a local RDF file and provides the possibility to fetch data from it by SPARQL queries.
    """

    def __init__(self, filename):
        self.__can_be_tree = False
        self.__can_be_tabular = True
        self.__graph__ = rdflib.Graph()
        self.__query__ = ""
        self.__filename__ = filename

    def __reduce_bound_triple_to_string_format(self, dict_of_bound_variables: dict):
        return {str(k): str(v) for k, v in dict_of_bound_variables.items()}

    def with_query(self, sparql_query: str) -> 'RDFFileDataSource':
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        self.__query__ = sparql_query
        return self

    def with_file(self, file: str) -> 'RDFFileDataSource':
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        self.__filename__ = file
        return self

    def _fetch_tabular(self):
        self.__graph__.parse(self.__filename__, format="turtle")
        result = self.__graph__.query(self.__query__)

        reduced_result_binding = [self.__reduce_bound_triple_to_string_format(t) for t in result.bindings]

        return pd.DataFrame(reduced_result_binding)

    def _fetch_tree(self):
        raise UnsupportedRepresentation("Only TABULAR representation is supported")

    def _can_be_tree(self) -> bool:
        return self.__can_be_tree

    def _can_be_tabular(self) -> bool:
        return self.__can_be_tabular

    def __str__(self):
        return f"from <...{str(self.__filename__)[-30:]}> {str(self.__query__)[:60]} ..."
