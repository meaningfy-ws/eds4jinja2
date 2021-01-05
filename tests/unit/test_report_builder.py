"""
test_jinja_builder.py
Date:  09/09/2020
Author: Laurentiu Mandru
Email: mclaurentiu79@gmail.com
"""

import pathlib
import shutil
from unittest.mock import Mock

import pytest
from eds4jinja2.builders.report_builder import ReportBuilder
from eds4jinja2.builders import deep_update
from bs4 import BeautifulSoup


@pytest.fixture(scope="function")
def sample_data_path() -> str:
    return pathlib.Path(__file__).parent.parent / "test_data/templates_test"


@pytest.fixture(scope="function")
def sample_data_path_latex() -> str:
    return pathlib.Path(__file__).parent.parent / "test_data/latex_templates_test"


def test_report_builder_config_file_not_found():
    with pytest.raises(FileNotFoundError) as exception:
        ReportBuilder(pathlib.Path.cwd())
    assert "No such file or directory" in str(exception.value)


def test_report_builder_config_file_exists(sample_data_path):
    ReportBuilder(sample_data_path)


def test_report_builder_flavour_config(sample_data_path):
    r = ReportBuilder(sample_data_path, additional_config={"template_flavour_syntax": "tex"})
    assert r.template_env.block_start_string == r'\BLOCK{'

    r = ReportBuilder(sample_data_path, additional_config={"template_flavour_syntax": "xml"})
    assert r.template_env.block_start_string == '{%'

    r = ReportBuilder(sample_data_path, additional_config={"template_flavour_syntax": ""})
    assert r.template_env.block_start_string == '{%'


def test_report_builder_make_document(sample_data_path):
    before_listener = Mock()
    after_listener = Mock()

    report_builder = ReportBuilder(target_path=sample_data_path, output_path=pathlib.Path(sample_data_path) / "output")

    report_builder.add_before_rendering_listener(before_listener)
    report_builder.add_after_rendering_listener(after_listener)

    report_builder.make_document()

    before_listener.assert_called_once()
    after_listener.assert_called_once()

    with open(pathlib.Path(sample_data_path) / "output" / "main.html", 'r') as htmlFile:
        parsed_html = BeautifulSoup(htmlFile.read())
        assert parsed_html.find("h1").text in "Cellar SPARQL endpoint fragment"

    path = pathlib.Path(sample_data_path) / "output"
    shutil.rmtree(path)


def test_report_builder_make_latex_document(sample_data_path_latex):
    out_path = sample_data_path_latex / "output"
    report_builder = ReportBuilder(target_path=sample_data_path_latex, output_path=out_path)
    report_builder.make_document()
    assert (out_path / "main.tex").exists()
    shutil.rmtree(out_path)


def test_deep_update():
    source = {'hello1': 1}
    overrides = {'hello2': 2}
    deep_update(source, overrides)
    assert source == {'hello1': 1, 'hello2': 2}

    source = {'hello': 'to_override'}
    overrides = {'hello': 'over'}
    deep_update(source, overrides)
    assert source == {'hello': 'over'}

    source = {'hello': {'value': 'to_override', 'no_change': 1}}
    overrides = {'hello': {'value': 'over'}}
    deep_update(source, overrides)
    assert source == {'hello': {'value': 'over', 'no_change': 1}}

    source = {'hello': {'value': 'to_override', 'no_change': 1}}
    overrides = {'hello': {'value': {}}}
    deep_update(source, overrides)
    assert source == {'hello': {'value': {}, 'no_change': 1}}

    source = {'hello': {'value': {}, 'no_change': 1}}
    overrides = {'hello': {'value': 2}}
    deep_update(source, overrides)
    assert source == {'hello': {'value': 2, 'no_change': 1}}
