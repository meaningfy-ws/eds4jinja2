"""
sparql_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from abc import ABC

from eds.adapters.base_data_source import DataSource, Representation


class SPARQLEndpointDataSource(DataSource, ABC):
    """
        Abstract class for fetching data from SPARQL endpoint. Graph name is optional.
    """

    def _query(self):
        """
            query a dataset and return the response or throw an error
        :return:
        """
        raise NotImplementedError


class SPARQLSelectDataSource(SPARQLEndpointDataSource):
    """
        Fetching data via SPARQL select statement from an endpoint. Graph name is optional.
    """
    raise NotImplementedError


class SPARQLDescribeDataSource(SPARQLEndpointDataSource):
    """
        Fetching data via SPARQL describe statement for a given URI resource from an endpoint. Graph name is optional.
    """
    raise NotImplementedError
