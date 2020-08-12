"""
base_data_source.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com

A generic data source.
"""
import enum
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class UnsupportedRepresentation(Exception):
    """
        Unsupported representation exception
    """


class DataSource(ABC):
    """
    generic data source
    """

    def fetch_tabular(self) -> Tuple[Optional[object], Optional[str]]:
        """
            read the content from the data source in tabular structure
        :return: a tuple where the first element is a result of a successful data reading and
                 the second is the error message in case of failure
        """
        try:
            if not self._can_be_tabular():
                raise UnsupportedRepresentation("Only TREE representation is supported")
            else:
                return self._fetch_tabular(), None
        except Exception as e:
            return None, str(e)

    def fetch_tree(self) -> Tuple[Optional[object], Optional[str]]:
        """
        read the content from the data source in tree structure
        :return: a tuple where the first element is a result of a successful data reading and
                 the second is the error message in case of failure
        """
        try:
            if not self._can_be_tree():
                raise UnsupportedRepresentation("Only TABULAR representation is supported")
            else:
                return self._fetch_tree(), None
        except Exception as e:
            return None, str(e)

    @abstractmethod
    def _can_be_tabular(self) -> bool:
        pass

    @abstractmethod
    def _can_be_tree(self) -> bool:
        pass

    @abstractmethod
    def _fetch_tabular(self):
        """
            fetch data and return as tabular representation
        :return:
        """
        pass

    @abstractmethod
    def _fetch_tree(self):
        """
            fetch data and return as tree representation
        :return:
        """
        pass
