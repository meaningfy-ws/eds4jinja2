# Date:  08/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: Data fetching from template

  Data can be fetched by specifications in the template

  Scenario: Fetch from SPARQL endpoint
    Given a SPARQL endpoint http://publications.europa.eu/webapi/rdf/sparql
    And a SPARQL query select * where {?s ?p ?o} limit 10
    When the resultset is requested from sparql endpoint
    Then the fetched content should be non empty
    And the content length is greater than 500
    And the returned error should be None


  Scenario Outline: Fetch from a local file
    Given a path to local <file> file
    When the resultset is requested as from_file <result_type>
    Then the returned error should be of type <error_fragment>
    And the fetched content should be <content_fragment>

    Examples:
      | file                             | result_type | content_fragment | error_fragment                        |
      | /tests/test_data/file.json       | tree        | non empty        | None                                  |
      | /tests/test_data/file.csv        | tabular     | non empty        | None                                  |
      | /tests/test_data/file.csv        | tree        | non empty        | None                                  |
#      | /tests/test_data/file.json       | tabular     | empty            | Only TREE representation is supported |
