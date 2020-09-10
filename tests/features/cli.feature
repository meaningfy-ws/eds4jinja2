# Date:  08/08/2020
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

Feature: CLI for report builder

  The CLI produces the desired output

  Scenario Outline: Generate a report from a template
    Given a path to a <directory>
    When the CLI is invoked
    Then <output> path contains the <file>
    And Then file contains the <content>

    Examples:
      | directory            | output                | file      | content                         |
      | templates_test       | templates_test/output | main.html | Cellar SPARQL endpoint fragment |