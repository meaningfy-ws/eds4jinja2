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

    # The 5xx -> error path (httpbin.org/status/500) was dropped: httpbin is unreliable (often
    # returns 503, not 500), making the assertion flaky. The error-surfacing behaviour is covered
    # by the unreachable-host case below; precise HTTP-status mapping is SPARQLWrapper's concern.
    Examples:
      | endpoint_reference                                     | query_text_reference                           | error_fragment        |
      | https://dc51efef6cca43debdb478b330dc7379.com           | select * where {?s ?p ?o} limit 10             | urlopen error         |
      | http://publications.europa.eu/webapi/rdf/sparql        | select *                                       |  QueryBadFormed       |


  Scenario Outline: Content of SPARQL select request for a tree structure
    Given a SPARQL endpoint http://publications.europa.eu/webapi/rdf/sparql
    And a SPARQL query select * where {?s ?p ?o} limit 10
    When the resultset is requested as tree
    Then the fetched content text should contain keys <content_keys>
    And the returned error should be None

    # comma separated values all of which shat shall be found
    Examples:
      | content_keys       |
      | 'bindings'         |
      | 'type'             |
      |'uri'               |
      |'value'             |
      | 's', 'p', 'o'      |

  Scenario Outline: Content of SPARQL select request for a tabular structure
    Given a SPARQL endpoint http://publications.europa.eu/webapi/rdf/sparql
    And a SPARQL query <query_text_reference>
    When the resultset is requested as tabular
    Then the fetched content text should contain values <content_values>
    And the returned error should be None

    # comma separated values all of which shat shall be found
    Examples:
      |query_text_reference | content_values                                                      |
      |select ?s ?o (<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> as ?i) where {?s a ?o} limit 10 | http://www.w3.org/1999/02/22-rdf-syntax-ns#type                     |
