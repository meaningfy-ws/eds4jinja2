# Date:  08/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: SPARQL fetching

  SPARQL query can be executed from the template

  Scenario Outline: SPARQL select request
    Given a SPARQL endpoint <endpoint_reference>
    And a SPARQL query <query_text_reference>
    When the resultset is rendered as <representation>
    Then the fetched content text should contain fragment <content_fragment>
    And the returned error should contain fragment <error_fragment>

    Examples:
      | endpoint_reference | query_text_reference              | content_fragment               | error_fragment        | representation |
      | local_correct      | spo_limit_10                      | 'bindings'                     |                       | tree           |
      | local_correct      | spo_limit_10                      | {'s': {'type': 'uri', 'value': |                       | tree           |
      | incorrect_address  | spo_limit_10                      |                                | EndPointNotFound      | tree           |
      | crashed_server     | spo_limit_10                      |                                | EndPointInternalError | tree           |
      | local_correct      | wrong_spo_limit_10                |                                | QueryBadFormed        | tree           |
      | local_correct      | query_longer_than_2048_characters |                                | URITooLong            | tree           |
      | local_correct      | spo_limit_10                      | http://                        |                       | tabular        |
