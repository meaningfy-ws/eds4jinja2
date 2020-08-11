"""
file_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from abc import ABC

from eds.adapters.base_data_source import DataSource, UnsupportedRepresentation


class FileDataSource(DataSource):
    """

    """

    def __init__(self, file_path):
        self.file_path = file_path
        self._determine_file_type()

    def _determine_file_type(self):
        # TODO: implement
        pass

    def _can_be_tabular(self) -> bool:
        # TODO: implement
        return True

    def _can_be_tree(self) -> bool:
        # TODO: implement
        return True

    def _fetch_tree(self):
        if not self._can_be_tree():
            raise UnsupportedRepresentation("Only TABULAR representation is supported")
        else:
            raise NotImplementedError

    def _fetch_tabular(self):
        if not self._can_be_tabular():
            raise UnsupportedRepresentation("Only TREE representation is supported")
        else:
            raise NotImplementedError
