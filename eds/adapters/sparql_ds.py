"""
sparql_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
import io
from typing import Optional

from SPARQLWrapper import SPARQLWrapper, JSON, CSV

from eds.adapters.base_data_source import DataSource
import pandas as pd

DEFAULT_ENCODING = 'utf-8'


class SPARQLEndpointDataSource(DataSource):
    """
        fetching data from SPARQL endpoint.
    """

    def __init__(self, endpoint_url):
        self.endpoint = SPARQLWrapper(endpoint_url)
        self.__can_be_tree = True
        self.__can_be_tabular = True

    def with_query(self, sparql_query: str) -> 'SPARQLEndpointDataSource':
        """
            set the query text and return the reference to self for chaining
        :return:
        """
        self.endpoint.setQuery(sparql_query)
        return self

    def with_uri(self, uri: str, graph_uri: Optional[str] = None) -> 'SPARQLEndpointDataSource':
        """
            set the query text and return the reference to self for chaining
        :return:
        """
        if graph_uri:
            self.endpoint.setQuery(f"DESCRIBE <{uri}> FROM <{graph_uri}>")
        else:
            self.endpoint.setQuery(f"DESCRIBE <{uri}>")
        return self

    def _fetch_tree(self):
        self.endpoint.setReturnFormat(JSON)
        query = self.endpoint.query()
        return query.convert()

    def _fetch_tabular(self):
        self.endpoint.setReturnFormat(CSV)
        query_result = self.endpoint.queryAndConvert()
        return pd.read_csv(io.StringIO(str(query_result, encoding=DEFAULT_ENCODING)))

    def _can_be_tree(self) -> bool:
        return self.__can_be_tree

    def _can_be_tabular(self) -> bool:
        return self.__can_be_tabular
