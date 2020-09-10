# coding=utf-8
"""File fetcher feature tests."""
import os
from pytest_bdd import (
    given,
    scenario,
    then,
    when, parsers,
)

from tests.steps.conftest import file_fetch_tree, file_fetch_tabular


@scenario('../features/file_ds.feature', 'Content of file requested as tabular structure')
def test_content_of_file_requested_as_tabular_structure():
    """Content of file requested as tabular structure."""


@scenario('../features/file_ds.feature', 'Content of file requested as tree structure')
def test_content_of_file_requested_as_tree_structure():
    """Content of file requested as tree structure."""


@scenario('../features/file_ds.feature', 'Errors of file request')
def test_errors_of_file_request():
    """Errors of file request."""


@given('a path to a <file>')
def a_path_to_a_file_state(scenarioContext, file):
    scenarioContext["filePath"] = os.getcwd() + file


@given(parsers.parse('a path to an CSV file containing a SPARQL resultset {filePath}'))
def a_path_to_an_csv_file_containing_a_sparql_resultset(scenarioContext, filePath):
    scenarioContext["filePath"] = os.getcwd() + filePath


@given(parsers.parse('a path to an JSON file containing a SPARQL resultset {filePath}'))
def a_path_to_an_json_file_containing_a_sparql_resultset(scenarioContext, filePath):
    scenarioContext["filePath"] = os.getcwd() + filePath


@when('the resultset is requested')
def the_resultset_is_requested(eds_environment, scenarioContext):
    renderedText = file_fetch_tree(eds_environment, scenarioContext["filePath"])
    # RENDER AS TREE AS WELL ?
    scenarioContext["renderedText"] = renderedText


@when('the resultset is requested as as tabular')
def the_resultset_is_requested_as_as_tabular(eds_environment, scenarioContext):
    renderedText = file_fetch_tabular(eds_environment, scenarioContext["filePath"])
    scenarioContext["renderedText"] = renderedText


@when('the resultset is requested as as tree')
def the_resultset_is_requested_as_as_tree(eds_environment, scenarioContext):
    renderedText = file_fetch_tree(eds_environment, scenarioContext["filePath"])
    scenarioContext["renderedText"] = renderedText


@then('Then the fetched content should be None')
def then_the_fetched_content_should_be_none(scenarioContext):
    assert "content:  None" in scenarioContext["renderedText"]


@then('Then the fetched content should contain <content_keys>')
def then_the_fetched_content_should_contain_content_keys(scenarioContext, content_keys):
    assert content_keys in scenarioContext["renderedText"]

@then('Then the fetched content should contain <content_values>')
def then_the_fetched_content_should_contain_content_values(scenarioContext, content_values):
    assert content_values in scenarioContext["renderedText"]


@then('the returned error should be None')
def the_returned_error_should_be_none(scenarioContext):
    assert "error: None" in scenarioContext["renderedText"]


@then('the returned error should contain <error_fragment>')
def the_returned_error_should_contain_error_fragment(scenarioContext, error_fragment):
    assert "error: " + error_fragment in scenarioContext["renderedText"]

