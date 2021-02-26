#!/usr/bin/python3

# namespace_handler.py
# Date:  25/02/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This module deals with namespace management over Pandas DataFrames.
    - Discovery of prefixes and namespaces in a DataFrame
    - prefix.cc lookup
    - Maintenance of a namespace inventory
    - Shortening of URIs to their QName forms
"""

import logging
from typing import List

import rdflib
from pandas import DataFrame

from eds4jinja2.adapters import invert_dict
from eds4jinja2.adapters.prefix_cc_fetcher import prefix_cc_lookup_base_uri

logger = logging.getLogger(__name__)


class NamespaceInventory(rdflib.namespace.NamespaceManager):

    def __init__(self, namespace_definition_dict=None):
        super().__init__(rdflib.Graph())

        if namespace_definition_dict:
            # reduce the namespace definition dictionary and bind the definitions
            for prefix, namespace in invert_dict(invert_dict(namespace_definition_dict)).items():
                self.bind(prefix=prefix, namespace=namespace, replace=True, override=True)

        self._remote_query_cash = []

    def namespaces_as_dict(self):
        """
        :return: return the namespace definitions as a dict
        """
        return {prefix: ns_uri.toPython() for prefix, ns_uri in self.namespaces()}

    def simplify_uris_in_tabular(self, data_frame: DataFrame, target_columns: List = None,
                                 prefix_cc_lookup=True, inplace=True, error_fail=True) -> DataFrame:
        """
            Replace the full URIs by their qname counterparts. Discover the namespaces
            in the process, if the namespaces are not defined.

        :param error_fail: fail on error or throw exception per data_fame cell
        :param inplace: indicate whether the current data_frame shall be modified or a new one be created instead
        :param prefix_cc_lookup:
        :param target_columns: the target columns to explore;
                                    Expectation is that these columns exclusively contain only URIs as values
        :param data_frame: the dataframe to explore
        :return:  the DataFrame with replaced values
        """
        if not target_columns:
            target_columns = []

        for col in target_columns:
            if col not in data_frame.columns.values.tolist():
                raise ValueError("The target column not found in the data frame")
        # get all the string columns
        obj_columns = data_frame.select_dtypes([object]).columns  # [1:]
        # limit to columns indicated in the self.target_columns
        obj_columns = filter(lambda x: x in target_columns, obj_columns) if target_columns else obj_columns

        # copy the dataframe if needed
        result_frame = data_frame if inplace else data_frame.copy(deep=True)
        for column in obj_columns:
            #
            result_frame[column] = result_frame[column].apply(
                lambda x: self.uri_to_qname(x, prefix_cc_lookup=prefix_cc_lookup, error_fail=error_fail))
        return result_frame

    def uri_to_qname(self, uri_string, prefix_cc_lookup=True, error_fail=False):
        """
            Transform the uri_string to a qname string and remember the namespace.
            If the namespace is not defined, the prefix can be looked up on prefix.cc
        :param error_fail: whether the errors shall fail hard or just issue a warning
        :param prefix_cc_lookup: whether to lookup a namespace on prefix.cc in case it is unknown or not.
        :param uri_string: the string of a URI to be reduced to a QName
        :return:
        """
        try:
            computed_ns = self.compute_qname_strict(uri_string)
            base_uri = computed_ns[1].toPython()
            if prefix_cc_lookup and base_uri not in self._remote_query_cash:
                self._remote_query_cash.append(base_uri)
                lookup_result = prefix_cc_lookup_base_uri(base_uri=base_uri)
                if lookup_result:
                    for prefix, namespace in lookup_result.items():  # expecting at most one result
                        self.bind(prefix=prefix, namespace=namespace, override=True, replace=True)
            self.reset()
            return self.qname_strict(uri_string)
        except Exception as e:
            logger.warning(f"Could not transform the URI <{uri_string}> to its QName form.")
            if error_fail:
                raise e

            return uri_string
