"""
test_jinja_builder.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""

import tests
from eds4jinja2.builders.jinja_builder import build_eds_environment


def test_dummy_template(eds_environment):
    template = eds_environment.from_string(tests.TEMPLATE_DUMMY)
    rendered_text = template.render()
    assert "content:  This is a static content" in rendered_text


def test_sparql_fetch_tabular_successful(eds_environment):
    template = eds_environment.from_string(tests.TEMPLATE_SPARQL_FETCH_TABULAR)
    rendered_text = template.render()
    assert "http://publications.europa.eu/resource/" in rendered_text
    # assert "[11 rows x 3 columns]" in rendered_text
    assert "error: None" in rendered_text


def test_sparql_fetch_tree_successful(eds_environment):
    template = eds_environment.from_string(tests.TEMPLATE_SPARQL_FETCH_TREE)
    rendered_text = template.render()
    assert 'http://publications.europa.eu/resource/authority/corporate-body/SPC' in rendered_text
    assert "['s', 'p', 'o']" in rendered_text
    assert "error: None"


def test_file_fetch_tree_successful(eds_environment):
    template = eds_environment.from_string(tests.TEMPLATE_FILE_FETCH_TREE)
    rendered_text = template.render()
    assert 'http://publications.europa.eu/resource/authority/corporate-body/SPC' in rendered_text
    assert "['s', 'p', 'o']" in rendered_text
    assert "error: None"


def test_file_fetch_tabular_successful(eds_environment):
    template = eds_environment.from_string(tests.TEMPLATE_FILE_FETCH_TABULAR)
    rendered_text = template.render()
    assert " http://publications.europa.eu/resource/" in rendered_text
    # assert "[11 rows x 3 columns]" in rendered_text
    assert "error: None" in rendered_text


def test_e2e_sparql_fetch_tree_successful():
    eds_environment = build_eds_environment()
    template = eds_environment.from_string(tests.TEMPLATE_SPARQL_FETCH_TREE)
    rendered_text = template.render(endpoint=tests.ENDPOINT_REMOTE_CORRECT, query_string=tests.SPO_LIMIT_10)
    assert len(rendered_text) > 1000
    assert "error: None" in rendered_text
