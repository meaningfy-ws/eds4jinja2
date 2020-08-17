#!/usr/bin/python3

# test_tabular_utils.py
# Date:  17/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

import pytest
from tabulate import tabulate
import pandas as pd
import numpy as np

pd.options.display.max_columns = None

from eds4jinja2.adapters.tabular_utils import invert_dict, replace_strings_in_tabular, add_relative_figures
from tests import RESPONSE_SPARQL_CSV_CORPORATE_BODY, RESPONSE_SPARQL_WITH_NUMBERS


@pytest.fixture(scope='function')
def dummy_df():
    return pd.DataFrame(RESPONSE_SPARQL_CSV_CORPORATE_BODY[1:], columns=RESPONSE_SPARQL_CSV_CORPORATE_BODY[0])


@pytest.fixture(scope='function')
def dummy_df_numbers():
    return pd.DataFrame(RESPONSE_SPARQL_WITH_NUMBERS[1:], columns=RESPONSE_SPARQL_WITH_NUMBERS[0])


@pytest.fixture
def dummy_prefixes():
    return {"rdf:": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "foaf:": "http://xmlns.com/foaf/0.1/",
            "yago:": "http://yago-knowledge.org/resource/",
            "rdfs:": "http://www.w3.org/2000/01/rdf-schema#",
            "dbo:": "http://dbpedia.org/ontology/",
            "dbp:": "http://dbpedia.org/property/",
            "dc:": "http://purl.org/dc/elements/1.1/",
            "owl:": "http://www.w3.org/2002/07/owl#",
            # "skos:": "http://www.w3.org/2004/02/skos/core#",
            "corporate-body:": "http://publications.europa.eu/resource/authority/corporate-body/",
            "euvoc:": "http://publications.europa.eu/ontology/euvoc#",
            "dcterms:": "http://purl.org/dc/terms/",
            "prov:": "http://www.w3.org/ns/prov#",
            "sioc:": "http://rdfs.org/sioc/ns#",
            "frbr:": "http://purl.org/vocab/frbr/core#",
            "xtypes:": "http://purl.org/xtypes/",
            "ont:": "http://purl.org/net/ns/ontology-annot#",
            "dct:": "http://purl.org/dc/terms/",
            }


@pytest.fixture
def dummy_namespaces(dummy_prefixes):
    return invert_dict(dummy_prefixes, True)


def test_invert_dict(dummy_prefixes):
    reduced_d = invert_dict(dummy_prefixes, True)
    assert "http://www.w3.org/2002/07/owl#" in reduced_d

    unreduced_d = invert_dict(dummy_prefixes, False)
    assert "dct:" in unreduced_d["http://purl.org/dc/terms/"]
    assert "dcterms:" in unreduced_d["http://purl.org/dc/terms/"]


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

