"""
conftest.py
Date:  11/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""

import pytest

from eds.builders.jinja_builder import get_eds_environment
from tests import FAKE_DATA_SOURCE_BUILDERS


@pytest.fixture(scope="function")
def eds_environment():
    return get_eds_environment(external_data_source_builders=FAKE_DATA_SOURCE_BUILDERS)
