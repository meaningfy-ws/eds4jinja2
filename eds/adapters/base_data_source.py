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

    def fetch(self, representation: Representation) -> Tuple[object, Optional[str]]:
        """
            read the content from the data source in either tree or tabular structure
        :type representation: specifies a representation of the read data: as tabular or tree
        :return: a tuple where the first element is a result of a successful data reading and
                 the second is the error message in case of failure
        """
        if representation is Representation.TREE:
            return self._fetch_tree()
        elif representation is Representation.TABULAR:
            return self._fetch_tabular()
        else:
            raise UnknownRepresentation(f"The representation {str(representation)} is not supported")

    def fetch_tabular(self) -> Tuple[object, Optional[str]]:
        if not self._can_be_tabular():
            raise UnsupportedRepresentation("Only TREE representation is supported")
        else:
            return self._fetch_tabular()

    def fetch_tree(self) -> Tuple[object, Optional[str]]:
        if not self._can_be_tree():
            raise UnsupportedRepresentation("Only TABULAR representation is supported")
        else:
            return self._fetch_tree()

    @abstractmethod
    def _can_be_tabular(self) -> bool:
        pass

    @abstractmethod
    def _can_be_tree(self) -> bool:
        pass

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
