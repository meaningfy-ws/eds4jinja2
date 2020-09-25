#!/usr/bin/python3

# remote_sparql_ds.py
# Date:  07/08/2020
# Author: Laurentiu Mandru
# Email: costezki.eugen@gmail.com


import pandas as pd
import rdflib

from eds4jinja2.adapters.base_data_source import DataSource, UnsupportedRepresentation

DEFAULT_ENCODING = 'utf-8'


class LocalSPARQLDataSource(DataSource):
    """
        Fetches data from SPARQL local datasource. Can be used either with a SPARQL query or a URI to be described.

        To query a SPARQL endpoint and get the results as *dict* object

        >>> ds = LocalSPARQLDataSource(sparql_endpoint_url)
        >>> dict_object = ds.with_query(sparql_query_text)._fetch_tree()

        unpack the content and error for a fail safe fetching
        >>> dict_object, error_string = ds.with_query(sparql_query_text).fetch_tree()

        To describe an URI and get the results as a pandas DataFrame

        >>> pd_dataframe = ds.with_uri(existent_uri)._fetch_tree()

        unpack the content and error for a fail safe fetching

        >>> pd_dataframe, error_string = ds.with_uri(existent_uri).fetch_tree()

        In case you want to target URI description from a Named Graph

        >>> pd_dataframe, error_string = ds.with_uri(existent_uri,named_graph).fetch_tree()
    """

    def __init__(self, filename):
        self.__can_be_tree = False
        self.__can_be_tabular = True
        self.__graph__ = rdflib.Graph()
        self.__query__ = ""
        self.__filename__ = filename

    def __reduce_bound_triple_to_string_format(self, dict_of_bound_variables: dict):
        return {str(k): str(v) for k, v in dict_of_bound_variables.items()}

    def with_query(self, sparql_query: str) -> 'LocalSPARQLDataSource':
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        self.__query__ = sparql_query
        return self

    def with_file(self, file: str) -> 'LocalSPARQLDataSource':
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
