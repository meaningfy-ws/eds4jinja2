#!/usr/bin/python3

# base_data_source.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" An abstract data source that is implemented by the specific ones. """

from abc import ABC, abstractmethod
from typing import Tuple, Optional


class UnsupportedRepresentation(Exception):
    """
        Unsupported representation exception
    """


class DataSource(ABC):
    """
        A generic data source that fetches data either in *tabular* or *tree* representation.

        The fail safe run is foreseen by default, to provide entire context back into the Template.

        >>> content, error = data_source.fetch_tabular()

        Exception prone running shall be performed with the underscored functions

        >>> content, error = data_source._fetch_tabular()

        To fetch a tree

        >>> content, error = data_source.fetch_tree()
    """

    def fetch_tabular(self) -> Tuple[Optional[object], Optional[str]]:
        """
            Read the content from the data source in tabular structure.

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
            Read the content from the data source and return a tree structure.

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
