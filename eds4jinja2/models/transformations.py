#!/usr/bin/python3

# transformations.py
# Pure text/tabular transformations used as Jinja filters and helpers (no I/O, no frameworks).

"""
Pure presentation/data transformations:

- :func:`escape_latex` — escape a string for LaTeX output (adapted from pappasam/latexbuild);
- :func:`replace_strings_in_tabular` / :func:`add_relative_figures` — polish a pandas DataFrame.
"""
import logging
import re
from typing import Dict, List

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_numeric_dtype

logger = logging.getLogger(__name__)

# --- LaTeX escaping ---------------------------------------------------------------------------

# All latex escape characters (EXCEPT "\", handled separately), escaping those that are special
# in PERL regular expressions.
ESCAPE_CHARS = [r'\&', '%', r'\$', '#', '_', r'\{', r'\}', '~', r'\^', ]

REGEX_ESCAPE_CHARS = [
    (re.compile(r"(?<!\\)" + i), r"\\" + i.replace('\\', ''))
    for i in ESCAPE_CHARS
]

ESCAPE_CHARS_OR = r'[{}\\]'.format(''.join(ESCAPE_CHARS))

REGEX_BACKSLASH = re.compile(r'(?<!\\)\\(?!{})'.format(ESCAPE_CHARS_OR))


def escape_latex(value: str):
    """ Escape a latex string. """
    if not isinstance(value, str):
        return value
    for regex, replace_text in REGEX_ESCAPE_CHARS:
        value = re.sub(regex, replace_text, value)
    value = re.sub(REGEX_BACKSLASH, r'\\\\', value)
    return value


# --- tabular (pandas) transformations ---------------------------------------------------------

def replace_strings_in_tabular(data_frame: pd.DataFrame, target_columns: List[str] = None,
                               value_mapping_dict: Dict = None,
                               mark_touched_rows: bool = False) -> List[str]:
    """
        Replaces the values from the target columns in a data frame according to the value-mapping dictionary.
        If mark_touched_rows is true, then adds a boolean column _touched_.

        >>> mapping_dict example = {"old value 1" : "new value 1", "old value 2":"new value 2"}

        :param mark_touched_rows: add a new boolean column _touched_ indicating which rows were updated
        :param value_mapping_dict: the string substitution mapping
        :param target_columns: a list of column names otehrwise leave empty if substitution applies to all columns
        :param data_frame: the data frame
        :return the list of unique strings found in the dataframe
    """
    if not target_columns:
        target_columns = []
    if not value_mapping_dict:
        value_mapping_dict = {}

    for col in target_columns:
        if col not in data_frame.columns.values.tolist():
            raise ValueError("The target column not found in the data frame")
    # get all the string columns
    obj_columns = data_frame.select_dtypes([object]).columns
    # limit to columns indicated in the target_columns
    if target_columns:
        obj_columns = [column for column in obj_columns if column in target_columns]

    # The URIs contains special regex chars, better to escape them when searching through dataframe
    escaped_value_mapping_dict = {r"" + re.escape(k): v for k, v in value_mapping_dict.items()}

    # add a column flagging touched rows
    if mark_touched_rows:
        mask = np.column_stack(
            [data_frame[col].str.contains('(' + '|'.join(escaped_value_mapping_dict.keys()) + ')', na=False)
             for col in obj_columns])
        data_frame["_touched_"] = np.logical_or.reduce(mask, axis=1)

    # which (unique) strings are found in the dataframe?
    strings_found_column_stack = np.array(
        [data_frame[col].str.findall('(' + '|'.join(escaped_value_mapping_dict.keys()) + ')',
                                     flags=re.IGNORECASE).values
         for col in obj_columns]
    )
    strings_found = np.unique(np.concatenate(strings_found_column_stack.flatten()))

    # nested dictionary that pandas replace understands: look in column for the value and replace it
    nested_dict = {column: escaped_value_mapping_dict for column in obj_columns}

    data_frame.replace(to_replace=None, regex=nested_dict, inplace=True)

    return strings_found


def add_relative_figures(data_frame: pd.DataFrame, target_columns: List[str], relativisers: List,  # noqa: C901
                         percentage: bool = True):
    """
        For each target_columns add a calculated column with relative values based on the relativisers.

    :param percentage:
    :param data_frame:
    :param target_columns:
    :param relativisers: a list of indicators corresponding to the *target_columns*
            comprising either *None*, a *number* or a *column name*
    :return:
    """
    # Some sanity checkers
    if len(relativisers) > len(target_columns):
        raise ValueError("There cannot be more relativisers than target columns")

    for rel in relativisers:
        if isinstance(rel, str):
            if rel not in data_frame.columns.values.tolist():
                raise ValueError("The relativiser column not found in the data frame")
            if not is_numeric_dtype(data_frame[rel]):
                raise ValueError("The relativiser column is not of numeric type")
        elif not (is_numeric_dtype(type(rel)) or rel is None):
            raise ValueError("The relativiser must be a number, None or a column name.")

    for col in target_columns:
        if col not in data_frame.columns.values.tolist():
            raise ValueError("The target column not found in the data frame")
        if not is_numeric_dtype(data_frame[col]):
            raise ValueError("The target column is not of numeric type")
    # End of sanity checkers

    new_columns = [c + "_relative" if not isinstance(r, str) else c + "_relative_to_" + r for c, r in
                   zip(target_columns, relativisers)]

    for (new_col, old_col, relativiser) in zip(new_columns, target_columns, relativisers):
        if not relativiser:
            relativiser = data_frame[old_col].sum()
        elif isinstance(relativiser, str):
            relativiser = data_frame[relativiser]

        if percentage:
            data_frame[new_col] = data_frame[old_col] * 100 / relativiser
        else:
            data_frame[new_col] = data_frame[old_col] / relativiser
