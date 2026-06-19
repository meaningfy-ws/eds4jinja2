#!/usr/bin/python3

# remote_sparql_ds.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com


import io
import threading
from typing import Optional

from SPARQLWrapper import SPARQLWrapper, JSON, CSV
from py_singleton import singleton

from eds4jinja2.models.data_source import DataSource
import pandas as pd

from eds4jinja2.models.sparql import build_query
from eds4jinja2.adapters.query_files import read_query_file

DEFAULT_ENCODING = 'utf-8'


@singleton
class SPARQLClientPool(object):
    """
        A singleton connection pool, that hosts a dictionary of endpoint_urls and
        a corresponding SPARQLWrapper object connecting to it.

        The rationale of this connection pool is to reuse connection objects and save time.

        The pool is **per-thread**: a SPARQLWrapper holds a mutable query string (``setQuery``),
        so sharing one wrapper across threads would let concurrent queries to the same endpoint
        clobber each other. Each thread therefore gets its own wrapper per endpoint — reused
        within the thread (single-threaded behaviour unchanged), isolated across threads. This
        makes the parallel report executor safe.
    """
    _local = threading.local()

    @staticmethod
    def _pool() -> dict:
        pool = getattr(SPARQLClientPool._local, "connection_pool", None)
        if pool is None:
            pool = {}
            SPARQLClientPool._local.connection_pool = pool
        return pool

    @staticmethod
    def create_or_reuse_connection(endpoint_url: str):
        pool = SPARQLClientPool._pool()
        if endpoint_url not in pool:
            pool[endpoint_url] = SPARQLWrapper(endpoint_url)
        return pool[endpoint_url]


# safe instantiation
SPARQLClientPool.instance()


class RemoteSPARQLEndpointDataSource(DataSource):
    """
        Fetches data from SPARQL endpoint. Can be used either with a SPARQL query or a URI to be described.

        To query a SPARQL endpoint and get the results as *dict* object

        >>> ds = RemoteSPARQLEndpointDataSource(sparql_endpoint_url)
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

    def __init__(self, endpoint_url):
        self.endpoint = SPARQLClientPool.create_or_reuse_connection(endpoint_url)
        self.__can_be_tree = True
        self.__can_be_tabular = True

    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'RemoteSPARQLEndpointDataSource':
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        self.endpoint.setQuery(build_query(sparql_query, substitution_variables, sparql_prefixes))
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'RemoteSPARQLEndpointDataSource':
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        self.endpoint.setQuery(
            build_query(read_query_file(sparql_query_file_path), substitution_variables, prefixes))
        return self

    def with_uri(self, uri: str, graph_uri: Optional[str] = None) -> 'RemoteSPARQLEndpointDataSource':
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        if graph_uri:
            self.endpoint.setQuery(f"DESCRIBE <{uri}> FROM <{graph_uri}>")
        else:
            self.endpoint.setQuery(f"DESCRIBE <{uri}>")
        return self

    def _fetch_tree(self):
        if not self.endpoint.queryString or self.endpoint.queryString.isspace():
            raise Exception("The query is empty.")

        self.endpoint.setReturnFormat(JSON)
        query = self.endpoint.query()
        return query.convert()

    def _fetch_tabular(self):
        if not self.endpoint.queryString or self.endpoint.queryString.isspace():
            raise Exception("The query is empty.")

        self.endpoint.setReturnFormat(CSV)
        query_result = self.endpoint.queryAndConvert()
        return pd.read_csv(io.StringIO(str(query_result, encoding=DEFAULT_ENCODING)))

    def _can_be_tree(self) -> bool:
        return self.__can_be_tree

    def _can_be_tabular(self) -> bool:
        return self.__can_be_tabular

    def __str__(self):
        return f"from <...{str(self.endpoint.endpoint)[-30:]}> {str(self.endpoint.queryString)[:60]} ..."
