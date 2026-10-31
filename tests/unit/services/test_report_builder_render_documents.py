"""
ReportBuilder.render_documents — one template, several named outputs, rendered to memory
(OpenSpec change `render-documents`, capability `batch-document-rendering`).
"""

import json

import pytest
import rdflib

from eds4jinja2.adapters.in_memory_sparql_ds import InMemorySPARQLDataSource
from eds4jinja2.services.report_builder import ReportBuilder

TTL = """
@prefix ex: <http://example.org/> .
ex:a a ex:Thing .
ex:b a ex:Thing .
ex:c a ex:Thing .
"""

FETCH = (
    "{% set rows, err = from_endpoint('x')"
    ".with_query('SELECT ?s WHERE { ?s a <http://example.org/Thing> }').fetch_tabular() %}"
)
DATA_TEMPLATE = FETCH + "{{ name }}:{{ rows | length }}"
# the record pass sees an empty placeholder and divides by zero; the real render sees 3 rows
RECORD_FAILS_TEMPLATE = FETCH + "{% if rows | length == 0 %}{{ 1 / 0 }}{% endif %}{{ name }}:{{ rows | length }}"


def _builder(tmp_path, template="{{ name }}", parallelism=1):
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "t.txt").write_text(template)
    config = {"template": "t.txt", "conf": {}, "parallelism": parallelism}
    (tmp_path / "config.json").write_text(json.dumps(config))
    graph = rdflib.Graph().parse(data=TTL, format="turtle")
    return ReportBuilder(
        tmp_path,
        output_path=tmp_path / "out",
        external_data_source_builders={"from_endpoint": lambda _e: InMemorySPARQLDataSource(graph)},
    )


def _listened(builder):
    calls = []
    builder.add_before_rendering_listener(lambda _c: calls.append("before"))
    builder.add_after_rendering_listener(lambda _c: calls.append("after"))
    return calls


def test_two_outputs_from_one_template(tmp_path):
    builder = _builder(tmp_path)
    calls = _listened(builder)
    texts = builder.render_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}})
    assert texts == {"a.txt": "A", "b.txt": "B"}
    assert list(texts) == ["a.txt", "b.txt"]
    assert not (tmp_path / "out").exists()
    assert calls == []


def test_conf_global_stays_available(tmp_path):
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "t.txt").write_text("{{ conf.title }}-{{ name }}")
    (tmp_path / "config.json").write_text(json.dumps({"template": "t.txt", "conf": {"title": "T"}}))
    assert ReportBuilder(tmp_path).render_documents({"a.txt": {"name": "A"}}) == {"a.txt": "T-A"}


def test_variable_named_conf_is_refused(tmp_path):
    with pytest.raises(ValueError, match="conf"):
        _builder(tmp_path).render_documents({"a.txt": {"conf": {}}})


def test_empty_batch(tmp_path):
    assert _builder(tmp_path).render_documents({}) == {}


@pytest.mark.parametrize("name", ["/tmp/x.txt", "../x.txt", ".", "g/../../x.txt"])
def test_names_that_leave_the_folder_are_refused(tmp_path, name):
    builder = _builder(tmp_path, template="{{ 1 / 0 }}")  # would raise ZeroDivisionError if rendered
    with pytest.raises(ValueError, match=name.replace(".", r"\.")):
        builder.render_documents({"ok.txt": {}, name: {}})


def test_sub_folder_name(tmp_path):
    assert _builder(tmp_path).render_documents({"g/a.txt": {"name": "A"}}) == {"g/a.txt": "A"}


def test_autoescape_for_one_batch_only(tmp_path):
    builder = _builder(tmp_path)
    assert builder.render_documents({"a.html": {"name": "<b>"}}, autoescape=True) == {"a.html": "&lt;b&gt;"}
    assert builder.render_documents({"a.txt": {"name": "<b>"}}) == {"a.txt": "<b>"}


def test_autoescape_restored_on_error(tmp_path):
    builder = _builder(tmp_path, template="{{ 1 / 0 }}")
    previous = builder.template_env.autoescape
    with pytest.raises(ZeroDivisionError):
        builder.render_documents({"a.txt": {}}, autoescape=not previous)
    assert builder.template_env.autoescape == previous


def test_parallel_batch_equals_sequential_batch(tmp_path_factory):
    batch = {"a.txt": {"name": "A"}, "b.txt": {"name": "B"}}
    seq = _builder(tmp_path_factory.mktemp("seq"), DATA_TEMPLATE, parallelism=1).render_documents(batch)
    par = _builder(tmp_path_factory.mktemp("par"), DATA_TEMPLATE, parallelism=4).render_documents(batch)
    assert seq == par == {"a.txt": "A:3", "b.txt": "B:3"}


def test_record_pass_fallback_stays_in_memory(tmp_path):
    builder = _builder(tmp_path, RECORD_FAILS_TEMPLATE, parallelism=4)
    calls = _listened(builder)
    assert builder.render_documents({"a.txt": {"name": "A"}}) == {"a.txt": "A:3"}
    assert not (tmp_path / "out").exists()
    assert calls == []


def test_make_document_after_parallel_batch_still_writes(tmp_path):
    builder = _builder(tmp_path, DATA_TEMPLATE, parallelism=4)
    builder.render_documents({"a.txt": {"name": "A"}})
    builder.make_document()
    assert (tmp_path / "out" / "t.txt").read_text() == ":3"
