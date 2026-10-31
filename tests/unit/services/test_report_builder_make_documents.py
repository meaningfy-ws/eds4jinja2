"""
ReportBuilder.make_documents — check every rendered output, then write them all
(OpenSpec change `make-documents`, capability `checked-document-writing`).
"""

import json

import pytest

from eds4jinja2.services.report_builder import ReportBuilder


def _builder(tmp_path, template="{{ name }}"):
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "t.txt").write_text(template)
    (tmp_path / "config.json").write_text(json.dumps({"template": "t.txt", "conf": {}}))
    return ReportBuilder(tmp_path, output_path=tmp_path / "out")


def _listened(builder):
    calls = []
    builder.add_before_rendering_listener(lambda _c: calls.append("before"))
    builder.add_after_rendering_listener(lambda _c: calls.append("after"))
    return calls


def _refuse(bad_name):
    def check(name, _text):
        if name == bad_name:
            raise SyntaxError("bad")

    return check


def test_all_checks_pass(tmp_path):
    seen = []
    paths = _builder(tmp_path).make_documents(
        {"a.txt": {"name": "A"}, "g/b.txt": {"name": "B"}}, check=lambda name, text: seen.append((name, text))
    )
    out = (tmp_path / "out").resolve()
    assert paths == [out / "a.txt", out / "g" / "b.txt"]
    assert (out / "a.txt").read_text(encoding="utf-8") == "A"
    assert (out / "g" / "b.txt").read_text(encoding="utf-8") == "B"
    assert seen == [("a.txt", "A"), ("g/b.txt", "B")]


def test_one_check_fails_nothing_written(tmp_path):
    with pytest.raises(SyntaxError, match="bad"):
        _builder(tmp_path).make_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}}, check=_refuse("b.txt"))
    assert not (tmp_path / "out" / "a.txt").exists()
    assert not (tmp_path / "out" / "b.txt").exists()


def test_no_check(tmp_path):
    _builder(tmp_path).make_documents({"a.txt": {"name": "A"}})
    assert (tmp_path / "out" / "a.txt").read_text(encoding="utf-8") == "A"


def test_utf8_text(tmp_path):
    _builder(tmp_path).make_documents({"a.txt": {"name": "ăîș→"}})
    assert (tmp_path / "out" / "a.txt").read_text(encoding="utf-8") == "ăîș→"


def test_autoescape_passed_through(tmp_path):
    _builder(tmp_path).make_documents({"a.html": {"name": "<b>"}}, autoescape=True)
    assert (tmp_path / "out" / "a.html").read_text(encoding="utf-8") == "&lt;b&gt;"


def test_listeners_once_per_batch(tmp_path):
    builder = _builder(tmp_path)
    calls = _listened(builder)
    builder.make_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}})
    assert calls == ["before", "after"]


def test_refused_batch_runs_no_after_listener(tmp_path):
    builder = _builder(tmp_path)
    calls = _listened(builder)
    with pytest.raises(SyntaxError):
        builder.make_documents({"a.txt": {"name": "A"}}, check=_refuse("a.txt"))
    assert calls == ["before"]


def test_render_failure_runs_no_after_listener(tmp_path):
    builder = _builder(tmp_path, template="{{ 1 / 0 }}")
    calls = _listened(builder)
    with pytest.raises(ZeroDivisionError):
        builder.make_documents({"a.txt": {}})
    assert calls == ["before"]
    assert not (tmp_path / "out" / "a.txt").exists()


def test_refused_name_runs_no_listener(tmp_path):
    builder = _builder(tmp_path)
    calls = _listened(builder)
    with pytest.raises(ValueError):
        builder.make_documents({"../x.txt": {"name": "A"}})
    assert calls == []


def test_empty_batch(tmp_path):
    builder = _builder(tmp_path)
    calls = _listened(builder)
    assert builder.make_documents({}) == []
    assert calls == []
