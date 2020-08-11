"""
dummy_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
# from eds.adapters import DataSource, Representation
from typing import Tuple, Optional

import pandas as pd

from eds.adapters.base_data_source import DataSource


class DummyDataSource(DataSource):
    """
        dummy data source returning a constant structure
    """

    def __init__(self, value=None):
        self.value

    def _fetch_tree(self) -> Tuple[object, Optional[str]]:
        return {"value": self.value}

    def _fetch_tabular(self) -> Tuple[object, Optional[str]]:
        if isinstance(self.value, (str, int)):
            return pd.Dataframe({"values": [self.value]})
        elif isinstance(self.value, (list, tuple, set)):
            return pd.Dataframe({"values": list(self.value)})
        elif isinstance(self.value, dict):
            return pd.Dataframe(self.value)
        else:
            raise TypeError(f"Unsupported type {type(self.value)}")
