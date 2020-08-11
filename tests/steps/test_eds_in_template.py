# coding=utf-8
"""Data fetching from template feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)


@scenario('../features/eds_in_template.feature', 'Fetch from SPARQL endpoint')
def test_fetch_from_sparql_endpoint():
    """Fetch from SPARQL endpoint."""


@scenario('../features/eds_in_template.feature', 'Fetch from a local file')
def test_fetch_from_a_local_file():
    """Fetch from a local file."""


@scenario('../features/eds_in_template.feature', 'Fetch from dummy data source')
def test_fetch_from_dummy_data_source():
    """Fetch from dummy data source."""


@given('a SPARQL endpoint LOCAL_CORRECT')
def a_sparql_endpoint_local_correct():
    """a SPARQL endpoint LOCAL_CORRECT."""
    raise NotImplementedError


@given('a SPARQL query SPO_LIMIT_10')
def a_sparql_query_spo_limit_10():
    """a SPARQL query SPO_LIMIT_10."""
    raise NotImplementedError


@given('a constant text value')
def a_constant_text_value():
    """a constant text value."""
    raise NotImplementedError


@given('a path to local <file_type> file')
def a_path_to_local_file_type_file():
    """a path to local <file_type> file."""
    raise NotImplementedError


@when('the resultset is requested as from_file <result_type>')
def the_resultset_is_requested_as_from_file_result_type():
    """the resultset is requested as from_file <result_type>."""
    raise NotImplementedError


@when('the resultset is requested from_sparql_endpoint')
def the_resultset_is_requested_from_sparql_endpoint():
    """the resultset is requested from_sparql_endpoint."""
    raise NotImplementedError


@when('the vlue is requested via a dummy datasource')
def the_vlue_is_requested_via_a_dummy_datasource():
    """the vlue is requested via a dummy datasource."""
    raise NotImplementedError


@then('the fetched content should be <content_fragment>')
def the_fetched_content_should_be_content_fragment():
    """the fetched content should be <content_fragment>."""
    raise NotImplementedError


@then('the fetched content should be non empty')
def the_fetched_content_should_be_non_empty():
    """the fetched content should be non empty."""
    raise NotImplementedError


@then('the fetched content should contain the initial value')
def the_fetched_content_should_contain_the_initial_value():
    """the fetched content should contain the initial value."""
    raise NotImplementedError


@then('the returned error should be None')
def the_returned_error_should_be_none():
    """the returned error should be None."""
    raise NotImplementedError


@then('the returned error should be of type <error_fragment>')
def the_returned_error_should_be_of_type_error_fragment():
    """the returned error should be of type <error_fragment>."""
    raise NotImplementedError

