"""
file_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from eds.adapters.base_data_source import DataSource, UnsupportedRepresentation


class TabularFileDataSource(DataSource):
    """
        Fetching data from a local file representing tabular data (CSV, Excel, Calc, etc.)
    """

    def _fetch_tree(self) -> (object, str):
        raise UnsupportedRepresentation("Only TABULAR representation is supported")


class TreeFileDataSource(DataSource):
    """
        Fetches data from a local file representing tree-like data structure (JSON, YAML, TOML, etc.)
    """

    def _fetch_tabular(self) -> (object, str):
        raise UnsupportedRepresentation("Only TREE representation is supported")
