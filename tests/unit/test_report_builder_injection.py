"""
test_report_builder_injection.py

Tests for the ReportBuilder builder-injection seam: external_data_source_builders /
external_filters are forwarded (merged over the defaults) into the Jinja environment.
"""
import pathlib

import pytest

from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource
from eds4jinja2.builders.report_builder import ReportBuilder


@pytest.fixture
def sample_data_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent.parent / "test_data/templates_test"


def test_no_injection_preserves_default_globals_and_filters(sample_data_path):
    rb = ReportBuilder(sample_data_path)
    for default_global in ("from_endpoint", "from_file", "from_rdf_file", "invert_dict"):
        assert default_global in rb.template_env.globals
    assert "escape_latex" in rb.template_env.filters


def test_injected_builder_overrides_default(sample_data_path):
    sentinel = object()
    rb = ReportBuilder(
        sample_data_path,
        external_data_source_builders={"from_endpoint": lambda _endpoint: sentinel})
    assert rb.template_env.globals["from_endpoint"]("ignored") is sentinel


def test_partial_injection_preserves_other_defaults(sample_data_path):
    rb = ReportBuilder(
        sample_data_path,
        external_data_source_builders={
            "from_endpoint": lambda _e: InMemorySPARQLDataSource(lambda q: None)})
    # the single override must not wipe the rest of the registry / filters
    assert "from_file" in rb.template_env.globals
    assert "invert_dict" in rb.template_env.globals
    assert "escape_latex" in rb.template_env.filters


def test_injected_filter_added(sample_data_path):
    rb = ReportBuilder(sample_data_path, external_filters={"shout": lambda s: str(s).upper()})
    assert rb.template_env.filters["shout"]("hi") == "HI"
    assert "escape_latex" in rb.template_env.filters  # default kept
