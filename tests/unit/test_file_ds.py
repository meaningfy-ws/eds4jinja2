"""
test_file_ds.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
import tempfile

import pytest

from eds.adapters.file_ds import FileDataSource

BASE_DIR = tempfile.TemporaryDirectory()
FILE_PATH_RELATIVE = ""
FILE_PATH_ABSOLUTE = ""

TABULAR_FILE_NAME_EXAMPLES = ["file.csv", "file.tsv", "file.xlsx", "file.xls", "file.ots", "file.fods"]
TREE_FILE_NAME_EXAMPLES = ["file.json", "file.yaml", "file.yml", "file.toml"]


@pytest.mark.parametrize("file_name", TABULAR_FILE_NAME_EXAMPLES)
def test_determine_tabular_file_type(file_name):
    fds = FileDataSource(file_path=file_name)
    assert fds._can_be_tabular()


@pytest.mark.parametrize("file_name", TREE_FILE_NAME_EXAMPLES)
def test_determine_tabular_file_type(file_name):
    fds = FileDataSource(file_path=file_name)
    assert fds._can_be_tree()


def test_open_relative_file_path():
    pass


def test_open_absolute_file_path():
    pass
