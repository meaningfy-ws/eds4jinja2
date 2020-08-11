# coding=utf-8
"""SPARQL query fetcher feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)


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
def a_sparql_endpoint_endpoint_reference():
    """a SPARQL endpoint <endpoint_reference>."""
    raise NotImplementedError


@given('a SPARQL query <query_text_reference>')
def a_sparql_query_query_text_reference():
    """a SPARQL query <query_text_reference>."""
    raise NotImplementedError


@when('the resultset is requested as tabular')
def the_resultset_is_requested_as_tabular():
    """the resultset is requested as tabular."""
    raise NotImplementedError


@when('the resultset is requested as tree')
def the_resultset_is_requested_as_tree():
    """the resultset is requested as tree."""
    raise NotImplementedError


@then('the fetched content should be None')
def the_fetched_content_should_be_none():
    """the fetched content should be None."""
    raise NotImplementedError


@then('the fetched content text should contain keys <content_keys>')
def the_fetched_content_text_should_contain_keys_content_keys():
    """the fetched content text should contain keys <content_keys>."""
    raise NotImplementedError


@then('the fetched content text should contain values <content_values>')
def the_fetched_content_text_should_contain_values_content_values():
    """the fetched content text should contain values <content_values>."""
    raise NotImplementedError


@then('the returned error should be None')
def the_returned_error_should_be_none():
    """the returned error should be None."""
    raise NotImplementedError


@then('the returned error should contain <error_fragment>')
def the_returned_error_should_contain_error_fragment():
    """the returned error should contain <error_fragment>."""
    raise NotImplementedError

