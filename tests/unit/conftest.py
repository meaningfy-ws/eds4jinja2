"""
conftest.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""

import pytest

from eds4jinja2.builders.jinja_builder import build_eds_environment
from tests import FAKE_DATA_SOURCE_BUILDERS


@pytest.fixture(scope="function")
def eds_environment():
    return build_eds_environment(external_data_source_builders=FAKE_DATA_SOURCE_BUILDERS)
