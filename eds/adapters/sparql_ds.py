"""
sparql_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from SPARQLWrapper import SPARQLWrapper, JSON, CSV

from eds.adapters.base_data_source import DataSource
from pandas import pd


class SPARQLEndpointDataSource(DataSource):
    """
        fetching data from SPARQL endpoint.
    """

    def __init__(self, endpoint_url):
        self.endpoint = SPARQLWrapper(endpoint_url)

    def query(self, sparql_query: str) -> 'SPARQLEndpointDataSource':
        """
            set the query text and return the reference to self for chaining
        :return:
        """
        self.endpoint.setQuery(sparql_query)
        return self

    def describe(self, uri: str, graph_uri: Optional[str] = None) -> 'SPARQLEndpointDataSource':
        """
            set the query text and return the reference to self for chaining
        :return:
        """
        if graph_uri:
            self.endpoint.setQuery(f"DESCRIBE <{uri}> FROM <{graph_uri}>")
        else:
            self.endpoint.setQuery(f"DESCRIBE <{uri}>")
        return self

    def _fetch_tree(self) -> Tuple[object, Optional[str]]:
        self.endpoint.setReturnFormat(JSON)
        query = self.endpoint.query()
        return query.convert(), None

    def _fetch_tabular(self) -> Tuple[object, Optional[str]]:
        self.endpoint.setReturnFormat(CSV)
        query = self.endpoint.query()
        return pd.read_csv(query.convert()), None

    def _can_be_tree(self) -> bool:
        return True

    def _can_be_tabular(self) -> bool:
        return True
