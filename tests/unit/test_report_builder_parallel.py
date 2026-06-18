"""
test_report_builder_parallel.py

Integration tests for the opt-in parallel pre-warm path of ReportBuilder. Uses an injected
in-memory graph (no network) so the test is deterministic, and asserts that parallel and
sequential renders produce identical output.
"""
import json

import rdflib

from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource
from eds4jinja2.builders.report_builder import ReportBuilder

TTL = """
@prefix ex: <http://example.org/> .
ex:a a ex:Thing .
ex:b a ex:Thing .
ex:c a ex:Thing .
"""

TEMPLATE = (
    "{% set rows, err = from_endpoint('x')"
    ".with_query('SELECT ?s WHERE { ?s a <http://example.org/Thing> }').fetch_tabular() %}"
    "Count:{{ rows | length }}"
)


def _scaffold(tmp_path, parallelism):
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "report.html").write_text(TEMPLATE)
    config = {"template": "report.html", "conf": {}, "parallelism": parallelism}
    (tmp_path / "config.json").write_text(json.dumps(config))
    return tmp_path


def _build(tmp_path, parallelism):
    graph = rdflib.Graph()
    graph.parse(data=TTL, format="turtle")
    target = _scaffold(tmp_path, parallelism)
    output = target / "out"
    rb = ReportBuilder(
        target, output_path=output,
        external_data_source_builders={"from_endpoint": lambda _e: InMemorySPARQLDataSource(graph)})
    rb.make_document()
    return (output / "report.html").read_text()


def test_parallel_render_produces_correct_output(tmp_path):
    assert _build(tmp_path, parallelism=4).strip() == "Count:3"


def test_parallel_and_sequential_outputs_match(tmp_path_factory):
    seq = _build(tmp_path_factory.mktemp("seq"), parallelism=1)
    par = _build(tmp_path_factory.mktemp("par"), parallelism=4)
    assert seq == par == "Count:3"


def test_no_prewarm_temp_dirs_leak(tmp_path):
    import tempfile
    before = set(p.name for p in __import__("pathlib").Path(tempfile.gettempdir()).glob("eds4jinja2-prewarm-*"))
    _build(tmp_path, parallelism=4)
    after = set(p.name for p in __import__("pathlib").Path(tempfile.gettempdir()).glob("eds4jinja2-prewarm-*"))
    assert after == before  # temp cache cleaned up
