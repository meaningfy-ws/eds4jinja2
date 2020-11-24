#!/usr/bin/python3

# __init__.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

__docformat__ = "restructuredtext en"

# The format of the __version__ line is matched by a regex in setup.py and /docs/conf.py
__version__ = "0.1.26"
__date__ = "2020-11-24"

import logging

from eds4jinja2.adapters.local_sparql_ds import RDFFileDataSource
from eds4jinja2.builders.jinja_builder import build_eds_environment, inject_environment_globals
from eds4jinja2.adapters.file_ds import FileDataSource
from eds4jinja2.adapters.remote_sparql_ds import RemoteSPARQLEndpointDataSource
from eds4jinja2.adapters.tabular_utils import invert_dict, add_relative_figures, replace_strings_in_tabular

# Making usage of this library more convenient
__all__ = ["build_eds_environment",
           "inject_environment_globals",
           "FileDataSource",
           "RemoteSPARQLEndpointDataSource",
           "RDFFileDataSource",
           "invert_dict",
           "add_relative_figures",
           "replace_strings_in_tabular",
           ]

# hard coding the log level and format
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
