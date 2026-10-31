"""
ReportBuilder.render_documents — one template, several named outputs, rendered to memory
(OpenSpec change `render-documents`, capability `batch-document-rendering`).
"""

import pytest

from tests.unit.services.conftest import listen

FETCH = (
    "{% set rows, err = from_endpoint('x')"
    ".with_query('SELECT ?s WHERE { ?s a <http://example.org/Thing> }').fetch_tabular() %}"
)
DATA_TEMPLATE = FETCH + "{{ name }}:{{ rows | length }}"
# the record pass sees an empty placeholder and divides by zero; the real render sees 3 rows
RECORD_FAILS_TEMPLATE = FETCH + "{% if rows | length == 0 %}{{ 1 / 0 }}{% endif %}{{ name }}:{{ rows | length }}"


def test_two_outputs_from_one_template(tmp_path, make_builder):
    builder = make_builder()
    calls = listen(builder)
    texts = builder.render_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}})
    assert texts == {"a.txt": "A", "b.txt": "B"}
    assert list(texts) == ["a.txt", "b.txt"]
    assert not (tmp_path / "out").exists()
    assert calls == []


def test_conf_global_stays_available(make_builder):
    builder = make_builder("{{ conf.title }}-{{ name }}", conf={"title": "T"})
    assert builder.render_documents({"a.txt": {"name": "A"}}) == {"a.txt": "T-A"}


def test_variable_named_conf_is_refused(make_builder):
    builder = make_builder(template="{{ 1 / 0 }}")  # would raise ZeroDivisionError if rendered
    with pytest.raises(ValueError, match="conf"):
        builder.render_documents({"ok.txt": {}, "a.txt": {"conf": {}}})


def test_empty_batch(tmp_path, make_builder):
    assert make_builder().render_documents({}) == {}


@pytest.mark.parametrize("name", ["/tmp/x.txt", "../x.txt", ".", "g/../../x.txt"])
def test_names_that_leave_the_folder_are_refused(tmp_path, make_builder, name):
    builder = make_builder(template="{{ 1 / 0 }}")  # would raise ZeroDivisionError if rendered
    with pytest.raises(ValueError, match=name.replace(".", r"\.")):
        builder.render_documents({"ok.txt": {}, name: {}})


def test_sub_folder_name(tmp_path, make_builder):
    assert make_builder().render_documents({"g/a.txt": {"name": "A"}}) == {"g/a.txt": "A"}


def test_autoescape_for_one_batch_only(tmp_path, make_builder):
    builder = make_builder()
    assert builder.render_documents({"a.html": {"name": "<b>"}}, autoescape=True) == {"a.html": "&lt;b&gt;"}
    assert builder.render_documents({"a.txt": {"name": "<b>"}}) == {"a.txt": "<b>"}


def test_autoescape_restored_on_error(tmp_path, make_builder):
    builder = make_builder(template="{{ 1 / 0 }}")
    previous = builder.template_env.autoescape
    with pytest.raises(ZeroDivisionError):
        builder.render_documents({"a.txt": {}}, autoescape=not previous)
    assert builder.template_env.autoescape == previous


def test_parallel_batch_equals_sequential_batch(tmp_path, make_builder):
    batch = {"a.txt": {"name": "A"}, "b.txt": {"name": "B"}}
    seq = make_builder(DATA_TEMPLATE, parallelism=1, root=tmp_path / "seq").render_documents(batch)
    par = make_builder(DATA_TEMPLATE, parallelism=4, root=tmp_path / "par").render_documents(batch)
    assert seq == par == {"a.txt": "A:3", "b.txt": "B:3"}


def test_record_pass_fallback_stays_in_memory(tmp_path, make_builder):
    builder = make_builder(RECORD_FAILS_TEMPLATE, parallelism=4)
    calls = listen(builder)
    assert builder.render_documents({"a.txt": {"name": "A"}}) == {"a.txt": "A:3"}
    assert not (tmp_path / "out").exists()
    assert calls == []


def test_make_document_after_parallel_batch_still_writes(tmp_path, make_builder):
    builder = make_builder(DATA_TEMPLATE, parallelism=4)
    builder.render_documents({"a.txt": {"name": "A"}})
    builder.make_document()
    assert (tmp_path / "out" / "t.txt").read_text() == ":3"


@pytest.mark.parametrize("twin", ["./a.txt", "g/../a.txt", "a.txt/"])
def test_names_of_the_same_file_are_refused(tmp_path, make_builder, twin):
    with pytest.raises(ValueError, match="same file"):
        make_builder(template="{{ 1 / 0 }}").render_documents({"a.txt": {}, twin: {}})


def test_unreadable_name_is_refused_naming_it(tmp_path, make_builder):
    with pytest.raises(ValueError, match="a.txt"):
        make_builder().render_documents({"a.txt\x00": {}})


def test_autoescape_batch_leaves_shared_environment_untouched(tmp_path, make_builder):
    builder = make_builder()
    previous = builder.template_env.autoescape
    builder.render_documents({"a.html": {"name": "<b>"}}, autoescape=not previous)
    assert builder.template_env.autoescape == previous
