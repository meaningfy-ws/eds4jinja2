# Date:  10/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: SPARQL query fetcher

  The data can be fetched from a SPARQL endpoint

  Scenario Outline: Errors of SPARQL select request
    Given a SPARQL endpoint <endpoint_reference>
    And a SPARQL query <query_text_reference>
    When the resultset is requested as tree
    Then the fetched content should be None
    And the returned error should contain <error_fragment>

    Examples:
      | endpoint_reference | query_text_reference              | error_fragment        |
      | inexistent_server  | spo_limit_10                      | EndPointNotFound      |
      | crashed_server     | spo_limit_10                      | EndPointInternalError |
      | local_correct      | wrong_spo_limit_10                | QueryBadFormed        |
      | local_correct      | query_longer_than_2048_characters | URITooLong            |


  Scenario Outline: Content of SPARQL select request for a tree structure
    Given a SPARQL endpoint <endpoint_reference>
    And a SPARQL query <query_text_reference>
    When the resultset is requested as tree
    Then the fetched content text should contain keys <content_keys>
    And the returned error should be None

    # comma separated values all of which shat shall be found
    Examples:
      | endpoint_reference | query_text_reference | content_keys     |
      | local_correct      | spo_limit_10         | bindings         |
      | local_correct      | spo_limit_10         | type, uri, value |
      | local_correct      | spo_limit_10         | s, p, o          |

  Scenario Outline: Content of SPARQL select request for a tabular structure
    Given a SPARQL endpoint <endpoint_reference>
    And a SPARQL query <query_text_reference>
    When the resultset is requested as tabular
    Then the fetched content text should contain values <content_values>
    And the returned error should be None

    # comma separated values all of which shat shall be found
    Examples:
      | endpoint_reference | query_text_reference | content_values                                                      |
      | local_correct      | spo_limit_10         | http://publications.europa.eu/resource/authority/corporate-body/SPC |
      | local_correct      | spo_limit_10         | http://www.w3.org/1999/02/22-rdf-syntax-ns#type                     |
      | local_correct      | spo_limit_10         | s, p , o                                                            |