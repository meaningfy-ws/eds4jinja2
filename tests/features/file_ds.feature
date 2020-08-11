# Date:  08/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: File fetcher

  The data can be fetched from a file source

  Scenario Outline: Errors of file request
    Given a path to a <file_state>
    When the resultset is requested
    Then Then the fetched content should be None
    And the returned error should contain <error_fragment>
    
    Examples:
      | file_state           | error_fragment    |
      | inexistent_file      | FileNotFoundError |
      | wrongly_encoded_file | ValueError        |

  Scenario Outline: Content of file requested as tree structure
    Given a path to an JSON file containing a SPARQL resultset
    When the resultset is requested as as tree
    Then Then the fetched content should contain <content_keys>
    And the returned error should be None

    # comma separated values all of which shat shall be found
    Examples:
      | content_keys     |
      | bindings         |
      | type, uri, value |
      | s, p, o          |


  Scenario Outline: Content of file requested as tabular structure
    Given a path to an CSV file containing a SPARQL resultset
    When the resultset is requested as as tabular
    Then Then the fetched content should contain <content_values>
    And the returned error should be None

    # comma separated values all of which shat shall be found
    Examples:
      | content_values                                                      |
      | http://publications.europa.eu/resource/authority/corporate-body/SPC |
      | http://www.w3.org/1999/02/22-rdf-syntax-ns#type                     |
      | s, p , o                                                            |