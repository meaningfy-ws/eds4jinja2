"""Shared fixtures for the ReportBuilder batch tests (render_documents / make_documents)."""

import json

import pytest
import rdflib

from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource
from eds4jinja2.services.report_builder import ReportBuilder

THINGS_TTL = """
@prefix ex: <http://example.org/> .
ex:a a ex:Thing .
ex:b a ex:Thing .
ex:c a ex:Thing .
"""


@pytest.fixture
def make_builder(tmp_path):
    """A one-template package `t.txt` under `root` (default tmp_path), output to root/out, with an in-memory
    `from_endpoint` serving three ex:Thing instances."""

    def make(template="{{ name }}", parallelism=1, conf=None, root=tmp_path):
        (root / "templates").mkdir(parents=True)
        (root / "templates" / "t.txt").write_text(template)
        config = {"template": "t.txt", "conf": conf or {}, "parallelism": parallelism}
        (root / "config.json").write_text(json.dumps(config))
        graph = rdflib.Graph().parse(data=THINGS_TTL, format="turtle")
        return ReportBuilder(
            root,
            output_path=root / "out",
            external_data_source_builders={"from_endpoint": lambda _e: InMemorySPARQLDataSource(graph)},
        )

    return make


def listen(builder) -> list[str]:
    """Record the builder's listener calls as "before"/"after"."""
    calls: list[str] = []
    builder.add_before_rendering_listener(lambda _c: calls.append("before"))
    builder.add_after_rendering_listener(lambda _c: calls.append("after"))
    return calls
