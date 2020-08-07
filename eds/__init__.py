"""
__init__.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from jinja2 import Environment

from eds.adapters.dummy_ds import DummyDataSource


def extend_environment(env: Environment):
    """
        Add the global variables to the environment
    :param env:
    :return:
    """
    env.globals['dummy_ds'] = lambda value=None: DummyDataSource(value)
