# coding=utf-8
"""Data fetching from template feature tests."""
import os

from pytest_bdd import (
    given,
    scenario,
    then,
    when, parsers,
)
from tests.steps.conftest import file_fetch_tabular, file_fetch_tree, sparql_fetch_tabular

# -------------------- HTTP-related steps --------------------
@scenario('../features/eds_in_template.feature', 'Fetch from SPARQL endpoint')
def test_fetch_from_sparql_endpoint():
    """Fetch from SPARQL endpoint."""

@given(parsers.parse('a SPARQL endpoint {endpointName}'))
def a_sparql_endpoint_local_correct(scenarioContext, endpointName):
    scenarioContext["endpoint"] = endpointName



@given(parsers.parse('a SPARQL query {sparqlQueryName}'))
def a_sparql_query_spo_limit_10(scenarioContext, sparqlQueryName):
    scenarioContext["sparqlQuery"] = sparqlQueryName

@when('the resultset is requested from sparql endpoint')
def the_resultset_is_requested_from_sparql_endpoint(scenarioContext, eds_environment):
    rendered_text = sparql_fetch_tabular(eds_environment, scenarioContext["endpoint"], scenarioContext["sparqlQuery"])
    scenarioContext["renderedText"] = rendered_text


@then('the fetched content should be non empty')
def the_fetched_content_should_be_non_empty(scenarioContext):
    assert scenarioContext["renderedText"] and scenarioContext["renderedText"].strip()

@then(parsers.parse('the returned error should be {returnedError}'))
def the_returned_error_should_be(scenarioContext, returnedError):
    assert "error: " + returnedError in scenarioContext["renderedText"]

@then(parsers.parse('the content length is greater than {length:d}'))
def and_the_content_length_is_greater_than(scenarioContext, length):
    assert len(scenarioContext["renderedText"]) > length


# --------------------  File-related steps --------------------
@scenario('../features/eds_in_template.feature', 'Fetch from a local file')
def test_fetch_from_a_local_file():
    """Fetch from a local file."""


@given('a path to local <file> file')
def a_path_to_local_file_type_file(scenarioContext, file):
    scenarioContext["filePath"] = os.getcwd() + file


@when('the resultset is requested as from_file <result_type>')
def the_resultset_is_requested_as_from_file_result_type(scenarioContext, eds_environment, result_type):
    scenarioContext["resultType"] = result_type

    if result_type == "tree":
        renderedText = file_fetch_tree(eds_environment, scenarioContext["filePath"])
    elif result_type == "tabular":
        renderedText = file_fetch_tabular(eds_environment, scenarioContext["filePath"])
    else:
        raise NotImplementedError("Only tree and tabular are supported.")

    scenarioContext["renderedText"] = renderedText


@then('the returned error should be of type <error_fragment>')
def the_returned_error_should_be_of_type_error_fragment(scenarioContext, error_fragment):
    assert "error: " + error_fragment in scenarioContext["renderedText"]


@then('the fetched content should be <content_fragment>')
def the_fetched_content_should_be_content_fragment(scenarioContext, content_fragment):
    if content_fragment == "non empty":
        assert "content:  None" not in scenarioContext["renderedText"]











