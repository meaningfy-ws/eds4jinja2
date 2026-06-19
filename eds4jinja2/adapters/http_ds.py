#!/usr/bin/python3
# http_ds.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

from eds4jinja2.models.data_source import DataSource


class HTTPDataSource(DataSource):
    """
        Fetching data by HTTP calls
    """
    # TODO: