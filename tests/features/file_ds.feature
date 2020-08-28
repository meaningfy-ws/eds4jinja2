# Date:  08/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: File fetcher

  The data can be fetched from a file source

  Scenario Outline: Errors of file request
    Given a path to a <file>
    When the resultset is requested
    Then the returned error should contain <error_fragment>
    And Then the fetched content should be None
    
    Examples:
      | file                                                    | error_fragment                           |
      | /tests/test_data/69a7ecbefc6d438e8d82ba123fadacad       | Only TABULAR representation is supported |
      | /tests/test_data/file.binary                            | Only TABULAR representation is supported |

  Scenario Outline: Content of file requested as tree structure
    Given a path to an JSON file containing a SPARQL resultset /tests/test_data/file.json
    When the resultset is requested as as tree
    Then Then the fetched content should contain <content_keys>
    And the returned error should be None

    # comma separated values all of which shall be found
    Examples:
      | content_keys       |
      | 'bindings'         |
      | 'type'             |
      | 'uri'              |
      | 'value'            |
      | 's', 'p', 'o'      |


  Scenario Outline: Content of file requested as tabular structure
    Given a path to an CSV file containing a SPARQL resultset /tests/test_data/file.csv
    When the resultset is requested as as tabular
    Then Then the fetched content should contain <content_values>
    And the returned error should be None

    # comma separated values all of which shall shall be found
    Examples:
      | content_values                                                      |
      | http://www.w3.org/2001/XMLSchema#gYear                              |
      | http://www.w3.org/1999/02/22-rdf-syntax-ns#type                     |
