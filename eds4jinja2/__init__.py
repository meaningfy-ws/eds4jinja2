#!/usr/bin/python3

# __init__.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

__docformat__ = "restructuredtext en"

# The __version__ literal is read by pyproject.toml ([tool.setuptools.dynamic]) and by a
# regex in /docs/conf.py — keep it a simple string assignment.
__version__ = "0.4.0"
__date__ = "2026-06-19"

import logging

from eds4jinja2.adapters.file_ds import FileDataSource
from eds4jinja2.adapters.graph_store import Engine, make_graph_store, RdflibGraphStore, OxigraphGraphStore
from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource
from eds4jinja2.adapters.local_sparql_ds import RDFFileDataSource
from eds4jinja2.adapters.namespace_handler import NamespaceInventory
from eds4jinja2.adapters.remote_sparql_ds import RemoteSPARQLEndpointDataSource
from eds4jinja2.adapters.tabular_utils import add_relative_figures, replace_strings_in_tabular
from eds4jinja2.builders.jinja_builder import build_eds_environment, inject_environment_globals

# Making usage of this library more convenient
__all__ = ["build_eds_environment",
           "inject_environment_globals",
           "FileDataSource",
           "RemoteSPARQLEndpointDataSource",
           "RDFFileDataSource",
           "InMemorySPARQLDataSource",
           "make_graph_store",
           "RdflibGraphStore",
           "OxigraphGraphStore",
           "Engine",
           "add_relative_figures",
           "replace_strings_in_tabular",
           "NamespaceInventory"
           ]

# hard coding the log level and format
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
