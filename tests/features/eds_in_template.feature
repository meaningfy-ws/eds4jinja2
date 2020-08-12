# Date:  08/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: Data fetching from template

  Data can be fetched by specifications in the template

  Scenario: Fetch from SPARQL endpoint
    Given a SPARQL endpoint LOCAL_CORRECT
    And a SPARQL query SPO_LIMIT_10
    When the resultset is requested from_sparql_endpoint
    Then the fetched content should be non empty
    And the returned error should be None

  Scenario Outline: Fetch from a local file
    Given a path to local <file_type> file
    When the resultset is requested as from_file <result_type>
    Then the fetched content should be <content_fragment>
    And the returned error should be of type <error_fragment>

    Examples:
      | file_type | result_type | content_fragment | error_fragment            |
      | JSON      | tree        | non empty        |                           |
      | CSV       | tabular     | non empty        |                           |
      | CSV       | tree        | non empty        |                           |
      | JSON      | tabular     |                  | UnsupportedRepresentation |
