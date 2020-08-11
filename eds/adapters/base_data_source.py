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


class Representation(enum.Enum):
    TABULAR = 1
    TREE = 2


class UnknownRepresentation(Exception):
    """
        Unknown representation exception
    """


class UnsupportedRepresentation(Exception):
    """
        Unsupported representation exception
    """


class DataSource(ABC):
    """
    generic data source
    """

    def fetch(self, _repr: Representation) -> Tuple[object, Optional[str]]:
        """
            read the content from the data source in either tree or tabular structure
        :type _repr: specifies a representation of the read data: as tabular or tree
        :return: a tuple where the first element is a result of a successful data reading and
                 the second is the error message in case of failure
        """
        if _repr is Representation.TREE:
            return self._fetch_tree()
        elif _repr is Representation.TABULAR:
            return self._fetch_tabular()
        else:
            raise UnknownRepresentation(f"The representation {str(_repr)} is not supported")

    def fetch_tabular(self) -> Tuple[object, Optional[str]]:
        return self._fetch_tabular()

    def fetch_tree(self) -> Tuple[object, Optional[str]]:
        return self._fetch_tree()

    @abstractmethod
    def _fetch_tabular(self) -> Tuple[object, Optional[str]]:
        """
            fetch data and return as tabular representation
        :return:
        """
        pass

    @abstractmethod
    def _fetch_tree(self) -> Tuple[object, Optional[str]]:
        """
            fetch data and return as tree representation
        :return:
        """
        pass
