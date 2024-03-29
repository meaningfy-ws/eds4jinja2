# coding=utf-8
"""CLI for report builder feature tests."""
import pathlib
import shutil

from bs4 import BeautifulSoup
from click.testing import CliRunner
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
    parsers
)

from eds4jinja2.entrypoints.cli.main import build_report

runner = CliRunner()


@scenario('../features/cli.feature', 'Generate a report from a template')
def test_generate_a_report_from_a_template():
    """Generate a report from a template."""


@given(parsers.parse('a path to a {directory}'))
def a_path_to_a_directory(scenarioContext, directory, sample_data_path):
    scenarioContext["input_path"] = pathlib.Path(sample_data_path) / directory


@when('the CLI is invoked')
def the_cli_is_invoked(scenarioContext):
    result = runner.invoke(build_report, ["--target", scenarioContext["input_path"], "--output",
                                          pathlib.Path(scenarioContext["input_path"]) / "output"])
    assert result.exit_code == 0
    assert not result.exception
    assert (pathlib.Path(scenarioContext["input_path"]) / "output" / "main.html").exists()


@then(parsers.parse('{output} path contains the {file}'))
def output_path_contains_the_file(scenarioContext, sample_data_path, output, file):
    scenarioContext["outputPath"] = pathlib.Path(sample_data_path) / output
    scenarioContext["outputFile"] = pathlib.Path(sample_data_path) / output / file
    assert pathlib.Path(scenarioContext["outputFile"]).is_file()


@then(parsers.parse('Then file contains the {content}'))
def then_file_contains_the_content(scenarioContext, content):
    with open(pathlib.Path(scenarioContext["outputFile"]), 'r') as htmlFile:
        parsed_html = BeautifulSoup(htmlFile.read())
        assert content in parsed_html.find("h1").text

    path = pathlib.Path(scenarioContext["outputPath"])
    shutil.rmtree(path)
