"""
test_jinja_builder.py
Date:  09/09/2020
Author: Laurentiu Mandru
Email: mclaurentiu79@gmail.com
"""

import pathlib
import shutil

import pytest
from eds4jinja2.builders.report_builder import ReportBuilder
from bs4 import BeautifulSoup


@pytest.fixture(scope="function")
def sample_data_path() -> str:
    return pathlib.Path(__file__).parent.parent / "test_data/templates_test"


before_fired = False
after_fired = False


def before_listener():
    global before_fired
    before_fired = True


def after_listener(static_folder, output_folder) -> bool:
    global after_fired
    after_fired = True


def test_report_builder_config_file_not_found():
    with pytest.raises(FileNotFoundError) as exception:
        ReportBuilder(pathlib.Path.cwd())
    assert "No such file or directory" in str(exception.value)


def test_report_builder_config_file_exists(sample_data_path):
    ReportBuilder(sample_data_path)


def test_report_builder_make_document(sample_data_path):
    global before_fired
    global after_fired
    report_builder = ReportBuilder(target_path=sample_data_path, output_path=sample_data_path)
    report_builder.add_before_rendering_listener(before_listener)
    report_builder.add_after_rendering_listener(after_listener)
    report_builder.make_document()

    assert before_fired is True
    assert after_fired is True

    with open(pathlib.Path(sample_data_path) / "output" / "main.html", 'r') as htmlFile:
        parsed_html = BeautifulSoup(htmlFile.read())
        assert parsed_html.find("h1").text in "Cellar SPARQL endpoint fragment"

    path = pathlib.Path(sample_data_path) / "output"
    shutil.rmtree(path)
