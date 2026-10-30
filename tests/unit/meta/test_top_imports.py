#!/usr/bin/python3

# test_top_imports.py
# Date:  17/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

"""just making sure that the eds4jinja2 provides a window to its functions and classes"""


def test_can_import_file_ds():
    from eds4jinja2 import FileDataSource

    assert FileDataSource(file_path="random") is not None
