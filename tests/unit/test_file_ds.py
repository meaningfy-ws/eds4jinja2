"""
test_file_ds.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
import pytest
import pathlib
from eds4jinja2.adapters.file_ds import FileDataSource

FILE_PATH_RELATIVE = ""
FILE_PATH_ABSOLUTE = ""

TABULAR_FILE_NAME_EXAMPLES = ["file.xlsx", "file.xls", "file.csv"]
TREE_FILE_NAME_EXAMPLES = ["file.json", "file.yaml"]

TEST_DATA_FOLDER = pathlib.Path(__file__).parents[1] / "test_data"


@pytest.mark.parametrize("file_name", TABULAR_FILE_NAME_EXAMPLES)
def test_determine_tabular_file_type(file_name):
    fds = FileDataSource(file_path=file_name)
    assert fds._can_be_tabular()


@pytest.mark.parametrize("file_name", TREE_FILE_NAME_EXAMPLES)
def test_determine_tabular_file_type(file_name):
    fds = FileDataSource(file_path=file_name)
    assert fds._can_be_tree()


@pytest.mark.parametrize("file_name", TABULAR_FILE_NAME_EXAMPLES)
def test_open_tabular_file_success(file_name):
    fds = FileDataSource(file_path=TEST_DATA_FOLDER / file_name)
    content, error = fds.fetch_tabular()
    assert content is not None
    assert error is None

    content, error = fds.fetch_tree()
    assert content is not None
    assert error is None


@pytest.mark.parametrize("file_name", TREE_FILE_NAME_EXAMPLES)
def test_open_tabular_file_failure(file_name):
    fds = FileDataSource(file_path=TEST_DATA_FOLDER / file_name)

    content, error = fds.fetch_tabular()
    assert content is None
    assert error is not None


@pytest.mark.parametrize("file_name", TREE_FILE_NAME_EXAMPLES)
def test_open_tree_file_success(file_name):
    fds = FileDataSource(file_path=TEST_DATA_FOLDER / file_name)
    content, error = fds.fetch_tree()
    assert content is not None
    assert error is None

    content, error = fds.fetch_tabular()
    assert content is None
    assert error is not None
