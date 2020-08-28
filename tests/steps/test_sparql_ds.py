# coding=utf-8
"""SPARQL query fetcher feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when, parsers,
)

from tests.steps.conftest import sparql_fetch_tree, sparql_fetch_tabular


@scenario('../features/sparql_ds.feature', 'Content of SPARQL select request for a tabular structure')
def test_content_of_sparql_select_request_for_a_tabular_structure():
    """Content of SPARQL select request for a tabular structure."""


@scenario('../features/sparql_ds.feature', 'Content of SPARQL select request for a tree structure')
def test_content_of_sparql_select_request_for_a_tree_structure():
    """Content of SPARQL select request for a tree structure."""


@scenario('../features/sparql_ds.feature', 'Errors of SPARQL select request')
def test_errors_of_sparql_select_request():
    """Errors of SPARQL select request."""


@given('a SPARQL endpoint <endpoint_reference>')
def a_sparql_endpoint_endpoint_reference(scenarioContext, endpoint_reference):
    scenarioContext["endpoint"] = endpoint_reference


@given(parsers.parse('a SPARQL endpoint {endpoint}'))
def a_sparql_endpoint_local_correct(scenarioContext, endpoint):
    scenarioContext["endpoint"] = endpoint


@given('a SPARQL query <query_text_reference>')
def a_sparql_query_query_text_reference(scenarioContext, query_text_reference):
    scenarioContext["query"] = query_text_reference


@given(parsers.parse('a SPARQL query {query}'))
def a_sparql_query_spo_limit_10(scenarioContext, query):
    scenarioContext["query"] = query


@when('the resultset is requested as tabular')
def the_resultset_is_requested_as_tabular(eds_environment, scenarioContext):
    renderedText = sparql_fetch_tabular(eds_environment, scenarioContext["endpoint"], scenarioContext["query"])
    scenarioContext["renderedText"] = renderedText


@when('the resultset is requested as tree')
def the_resultset_is_requested_as_tree(eds_environment, scenarioContext):
    renderedText = sparql_fetch_tree(eds_environment, scenarioContext["endpoint"], scenarioContext["query"])
    scenarioContext["renderedText"] = renderedText


@then('the fetched content should be None')
def the_fetched_content_should_be_none(scenarioContext):
    assert "content:  None" in scenarioContext["renderedText"]



@then('the fetched content text should contain keys <content_keys>')
def the_fetched_content_text_should_contain_keys_content_keys(scenarioContext, content_keys):
    assert content_keys in scenarioContext["renderedText"]


@then('the fetched content text should contain values <content_values>')
def the_fetched_content_text_should_contain_values_content_values(scenarioContext, content_values):
    assert content_values in scenarioContext["renderedText"]



@then('the returned error should be None')
def the_returned_error_should_be_none(scenarioContext):
    assert "error: None" in scenarioContext["renderedText"]


@then('the returned error should contain <error_fragment>')
def the_returned_error_should_contain_error_fragment(scenarioContext, error_fragment):
    assert error_fragment in scenarioContext["renderedText"]