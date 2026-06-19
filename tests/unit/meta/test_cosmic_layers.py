"""
test_cosmic_layers.py

Guards the Cosmic-Python restructure: the top-level public API stays stable across the move,
the version signals the breaking bump, and the models layer is importable in isolation (its
purity is additionally enforced by import-linter / `make check-architecture`).
"""
import importlib

import pytest

import eds4jinja2

EXPECTED_PUBLIC_API = {
    "build_eds_environment", "inject_environment_globals", "FileDataSource",
    "RemoteSPARQLEndpointDataSource", "RDFFileDataSource", "InMemorySPARQLDataSource",
    "make_graph_store", "RdflibGraphStore", "OxigraphGraphStore", "Engine",
    "add_relative_figures", "replace_strings_in_tabular", "NamespaceInventory",
}


def test_public_api_names_still_importable():
    for name in EXPECTED_PUBLIC_API:
        assert hasattr(eds4jinja2, name), f"public name {name} missing from eds4jinja2"


def test_public_all_is_the_expected_set():
    assert set(eds4jinja2.__all__) == EXPECTED_PUBLIC_API


def test_version_is_major_one():
    assert eds4jinja2.__version__ == "1.0.0"


@pytest.mark.parametrize("module", [
    "eds4jinja2.models.sparql",
    "eds4jinja2.models.data_source",
    "eds4jinja2.models.transformations",
    "eds4jinja2.models.collections",
])
def test_models_modules_import_in_isolation(module):
    # pure domain modules must import without dragging in adapters/services/entrypoints
    assert importlib.import_module(module) is not None


def test_layer_modules_resolve():
    for module in ("eds4jinja2.adapters.graph_store", "eds4jinja2.adapters.query_files",
                   "eds4jinja2.services.report_builder", "eds4jinja2.services.jinja_builder",
                   "eds4jinja2.entrypoints.cli.main"):
        assert importlib.import_module(module) is not None
