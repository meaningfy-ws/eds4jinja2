"""
ReportBuilder.make_documents — check every rendered output, then write them all
(OpenSpec change `make-documents`, capability `checked-document-writing`).
"""

import pytest

from tests.unit.services.conftest import listen


def _refuse(bad_name):
    def check(name, _text):
        if name == bad_name:
            raise SyntaxError("bad")

    return check


def test_all_checks_pass(tmp_path, make_builder):
    seen = []
    paths = make_builder().make_documents(
        {"a.txt": {"name": "A"}, "g/b.txt": {"name": "B"}}, check=lambda name, text: seen.append((name, text))
    )
    out = (tmp_path / "out").resolve()
    assert paths == [out / "a.txt", out / "g" / "b.txt"]
    assert (out / "a.txt").read_text(encoding="utf-8") == "A"
    assert (out / "g" / "b.txt").read_text(encoding="utf-8") == "B"
    assert seen == [("a.txt", "A"), ("g/b.txt", "B")]


def test_one_check_fails_nothing_written(tmp_path, make_builder):
    refusal = SyntaxError("bad")

    def check(name, _text):
        if name == "b.txt":
            raise refusal

    with pytest.raises(SyntaxError) as raised:
        make_builder().make_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}}, check=check)
    assert raised.value is refusal  # propagated unchanged
    assert not (tmp_path / "out" / "a.txt").exists()
    assert not (tmp_path / "out" / "b.txt").exists()


def test_no_check(tmp_path, make_builder):
    make_builder().make_documents({"a.txt": {"name": "A"}})
    assert (tmp_path / "out" / "a.txt").read_text(encoding="utf-8") == "A"


def test_utf8_text(tmp_path, make_builder):
    make_builder().make_documents({"a.txt": {"name": "ăîș→"}})
    assert (tmp_path / "out" / "a.txt").read_text(encoding="utf-8") == "ăîș→"


def test_autoescape_passed_through(tmp_path, make_builder):
    make_builder().make_documents({"a.html": {"name": "<b>"}}, autoescape=True)
    assert (tmp_path / "out" / "a.html").read_text(encoding="utf-8") == "&lt;b&gt;"


def test_listeners_once_per_batch(tmp_path, make_builder):
    builder = make_builder()
    calls = listen(builder)
    builder.make_documents({"a.txt": {"name": "A"}, "b.txt": {"name": "B"}})
    assert calls == ["before", "after"]


def test_refused_batch_runs_no_after_listener(tmp_path, make_builder):
    builder = make_builder()
    calls = listen(builder)
    with pytest.raises(SyntaxError):
        builder.make_documents({"a.txt": {"name": "A"}}, check=_refuse("a.txt"))
    assert calls == ["before"]


def test_render_failure_runs_no_after_listener(tmp_path, make_builder):
    builder = make_builder(template="{{ 1 / 0 }}")
    calls = listen(builder)
    with pytest.raises(ZeroDivisionError):
        builder.make_documents({"a.txt": {}})
    assert calls == ["before"]
    assert not (tmp_path / "out" / "a.txt").exists()


def test_refused_name_runs_no_listener(tmp_path, make_builder):
    builder = make_builder()
    calls = listen(builder)
    with pytest.raises(ValueError):
        builder.make_documents({"../x.txt": {"name": "A"}})
    assert calls == []


def test_empty_batch(tmp_path, make_builder):
    builder = make_builder()
    calls = listen(builder)
    assert builder.make_documents({}) == []
    assert calls == []


def test_names_of_the_same_file_write_nothing(tmp_path, make_builder):
    builder = make_builder()
    calls = listen(builder)
    with pytest.raises(ValueError, match="same file"):
        builder.make_documents({"a.txt": {"name": "1"}, "./a.txt": {"name": "2"}})
    assert not (tmp_path / "out" / "a.txt").exists()
    assert calls == []
