"""
http_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from eds.adapters.base_data_source import DataSource, Representation


class HTTPDataSource(DataSource):
    """
        Fetching data by HTTP calls
    """
    # TODO: