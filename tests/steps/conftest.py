# conftest.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
import pathlib

import pytest

import tests
from eds4jinja2 import build_eds_environment


@pytest.fixture(scope="session")
def scenarioContext():
    return {}


@pytest.fixture(scope="function")
def eds_environment():
    return build_eds_environment()


@pytest.fixture(scope="function")
def sample_data_path() -> str:
    return pathlib.Path(__file__).parent.parent / "test_data"

def sparql_fetch_tree(eds_environment, endpoint, sparqlQuery):
    template = eds_environment.from_string(tests.TEMPLATE_SPARQL_FETCH_TREE)
    rendered_text = template.render(endpoint=endpoint,query_string=sparqlQuery)
    return rendered_text


def sparql_fetch_tabular(eds_environment, endpoint, sparqlQuery):
    template = eds_environment.from_string(tests.TEMPLATE_SPARQL_FETCH_TABULAR)
    rendered_text = template.render(endpoint=endpoint,query_string=sparqlQuery)
    return rendered_text

def file_fetch_tree(eds_environment, filePath):
    template = eds_environment.from_string(tests.TEMPLATE_FILE_FETCH_TREE)
    rendered_text = template.render(path=filePath)
    return rendered_text


def file_fetch_tabular(eds_environment, filePath):
    template = eds_environment.from_string(tests.TEMPLATE_FILE_FETCH_TABULAR)
    rendered_text = template.render(path=filePath)
    return rendered_text
