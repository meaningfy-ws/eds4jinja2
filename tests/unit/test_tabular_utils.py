#!/usr/bin/python3

# test_tabular_utils.py
# Date:  17/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

import pandas as pd
import pytest

from eds4jinja2.adapters.tabular_utils import replace_strings_in_tabular, add_relative_figures

pd.options.display.max_columns = None


def test_replace_strings_in_tabular(dummy_df, dummy_namespaces):
    replace_strings_in_tabular(dummy_df, target_columns=['s'], value_mapping_dict=dummy_namespaces,
                               mark_touched_rows=True)
    assert dummy_df['s'].str.contains("corporate-body:SPC", na=False).any()
    assert not dummy_df['o'].str.contains("euvoc:Corporate", na=False).any()
    assert not dummy_df['p'].str.contains("rdf:type", na=False).any()


def test_replace_strings_in_tabular2(dummy_df, dummy_namespaces):
    replace_strings_in_tabular(dummy_df, target_columns=[], value_mapping_dict=dummy_namespaces,
                               mark_touched_rows=True)
    assert dummy_df['o'].str.contains("euvoc:Corporate", na=False).any()
    assert dummy_df['s'].str.contains("corporate-body:SPC", na=False).any()
    assert dummy_df['p'].str.contains("rdf:type", na=False).any()
    assert dummy_df['_touched_'].all()


def test_count_string_replacement(dummy_df, dummy_namespaces):
    strings_found = replace_strings_in_tabular(dummy_df, target_columns=[], value_mapping_dict=dummy_namespaces,
                                               mark_touched_rows=True)
    assert "http://publications.europa.eu/ontology/euvoc#" in strings_found
    assert "http://publications.europa.eu/resource/authority/corporate-body/" in strings_found
    assert "http://www.w3.org/1999/02/22-rdf-syntax-ns#" in strings_found


def test_make_relative(dummy_df_numbers):
    add_relative_figures(dummy_df_numbers, target_columns=['subject_cnt', 'pattern_cnt'], relativisers=[100, None],
                         percentage=False)
    assert dummy_df_numbers.loc[0, 'subject_cnt_relative'] == 1.04
    assert round(dummy_df_numbers.loc[0, 'pattern_cnt_relative'], ndigits=3) == round(0.00387832, ndigits=3)

    add_relative_figures(dummy_df_numbers, target_columns=['subject_cnt', 'pattern_cnt'], relativisers=[100, None],
                         percentage=True)
    assert dummy_df_numbers.loc[0, 'subject_cnt_relative'] == 1.04 * 100
    assert round(dummy_df_numbers.loc[0, 'pattern_cnt_relative'], ndigits=3) == round(0.00387832 * 100, ndigits=3)


def test_make_relative(dummy_df_numbers):
    with pytest.raises(ValueError):
        add_relative_figures(dummy_df_numbers, target_columns=['subject_cnt', 'pattern_cnt'],
                             relativisers=[100, None, None],
                             percentage=True)
    with pytest.raises(ValueError):
        add_relative_figures(dummy_df_numbers, target_columns=['subject_cnt', 'pattern_cnt'],
                             relativisers=[5, 'qwe'],
                             percentage=True)
    with pytest.raises(ValueError):
        add_relative_figures(dummy_df_numbers, target_columns=['subject_cnt', 'pattern_cnt'],
                             relativisers=[5, {}],
                             percentage=True)
    with pytest.raises(ValueError):
        add_relative_figures(dummy_df_numbers, target_columns=['subject_cnt', 'pattern_cnt'],
                             relativisers=[5, 'property'],
                             percentage=True)
    # print('\n\n\n')
    # print(tabulate(dummy_df_numbers, headers='keys'))
