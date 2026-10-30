"""
test_file_ds.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""

import pathlib

import pytest

import tests
from eds4jinja2.adapters.file_ds import FileDataSource

FILE_PATH_RELATIVE = ""
FILE_PATH_ABSOLUTE = ""

TABULAR_FILE_NAME_EXAMPLES = ["file.xlsx", "file.xls", "file.csv"]
TREE_FILE_NAME_EXAMPLES = ["file.json", "file.yaml"]

# Anchored on the `tests` package so it is stable regardless of this file's sub-folder.
TEST_DATA_FOLDER = pathlib.Path(tests.__file__).parent / "test_data"


@pytest.mark.parametrize("file_name", TABULAR_FILE_NAME_EXAMPLES)
def test_determine_tabular_file_type(file_name):
    fds = FileDataSource(file_path=file_name)
    assert fds._can_be_tabular()


@pytest.mark.parametrize("file_name", TREE_FILE_NAME_EXAMPLES)
def test_determine_tree_file_type(file_name):
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
    print(TEST_DATA_FOLDER / file_name)
    fds = FileDataSource(file_path=TEST_DATA_FOLDER / file_name)
    content, error = fds.fetch_tree()
    assert content is not None
    assert error is None

    # content, error = fds.fetch_tabular()
    # assert content is None
    # assert error is not None


def test_fetch_toml_as_tree(tmp_path):
    toml_file = tmp_path / "file.toml"
    toml_file.write_text('a = 1\nname = "Ștefan"\n[b]\nc = "d"\n', encoding="utf-8")
    content, error = FileDataSource(file_path=toml_file).fetch_tree()
    assert error is None
    assert content == {"a": 1, "name": "Ștefan", "b": {"c": "d"}}


def test_fetch_empty_toml_as_tree(tmp_path):
    toml_file = tmp_path / "empty.toml"
    toml_file.write_text("", encoding="utf-8")
    content, error = FileDataSource(file_path=toml_file).fetch_tree()
    assert error is None
    assert content == {}


def test_fetch_invalid_toml_fails_safe(tmp_path):
    toml_file = tmp_path / "invalid.toml"
    toml_file.write_text("a = ", encoding="utf-8")
    content, error = FileDataSource(file_path=toml_file).fetch_tree()
    assert content is None
    assert error
