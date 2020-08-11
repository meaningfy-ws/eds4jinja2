# coding=utf-8
"""File fetcher feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)


@scenario('../features/file_ds.feature', 'Content of file requested as tabular structure')
def test_content_of_file_requested_as_tabular_structure():
    """Content of file requested as tabular structure."""


@scenario('../features/file_ds.feature', 'Content of file requested as tree structure')
def test_content_of_file_requested_as_tree_structure():
    """Content of file requested as tree structure."""


@scenario('../features/file_ds.feature', 'Errors of file request')
def test_errors_of_file_request():
    """Errors of file request."""


@given('a path to a <file_state>')
def a_path_to_a_file_state():
    """a path to a <file_state>."""
    raise NotImplementedError


@given('a path to an CSV file containing a SPARQL resultset')
def a_path_to_an_csv_file_containing_a_sparql_resultset():
    """a path to an CSV file containing a SPARQL resultset."""
    raise NotImplementedError


@given('a path to an JSON file containing a SPARQL resultset')
def a_path_to_an_json_file_containing_a_sparql_resultset():
    """a path to an JSON file containing a SPARQL resultset."""
    raise NotImplementedError


@when('the resultset is requested')
def the_resultset_is_requested():
    """the resultset is requested."""
    raise NotImplementedError


@when('the resultset is requested as as tabular')
def the_resultset_is_requested_as_as_tabular():
    """the resultset is requested as as tabular."""
    raise NotImplementedError


@when('the resultset is requested as as tree')
def the_resultset_is_requested_as_as_tree():
    """the resultset is requested as as tree."""
    raise NotImplementedError


@then('Then the fetched content should be None')
def then_the_fetched_content_should_be_none():
    """Then the fetched content should be None."""
    raise NotImplementedError


@then('Then the fetched content should contain <content_keys>')
def then_the_fetched_content_should_contain_content_keys():
    """Then the fetched content should contain <content_keys>."""
    raise NotImplementedError


@then('Then the fetched content should contain <content_values>')
def then_the_fetched_content_should_contain_content_values():
    """Then the fetched content should contain <content_values>."""
    raise NotImplementedError


@then('the returned error should be None')
def the_returned_error_should_be_none():
    """the returned error should be None."""
    raise NotImplementedError


@then('the returned error should contain <error_fragment>')
def the_returned_error_should_contain_error_fragment():
    """the returned error should contain <error_fragment>."""
    raise NotImplementedError

