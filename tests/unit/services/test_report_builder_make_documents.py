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


def test_bytes_on_disk_are_the_checked_text(tmp_path, make_builder):
    accepted = {}
    make_builder("line 1\r\nline 2\nline 3{{ name }}").make_documents(
        {"a.txt": {"name": "\n"}}, check=lambda name, text: accepted.update({name: text})
    )
    assert (tmp_path / "out" / "a.txt").read_bytes() == accepted["a.txt"].encode("utf-8")


def test_existing_file_is_overwritten_and_others_untouched(tmp_path, make_builder):
    builder = make_builder()
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "a.txt").write_text("old")
    (tmp_path / "out" / "keep.txt").write_text("keep")
    builder.make_documents({"a.txt": {"name": "new"}})
    assert (tmp_path / "out" / "a.txt").read_text() == "new"
    assert (tmp_path / "out" / "keep.txt").read_text() == "keep"


def test_checks_stop_at_the_first_failure(make_builder):
    seen = []

    def check(name, _text):
        seen.append(name)
        if name == "b.txt":
            raise SyntaxError("bad")

    with pytest.raises(SyntaxError):
        make_builder().make_documents({"a.txt": {}, "b.txt": {}, "c.txt": {}}, check=check)
    assert seen == ["a.txt", "b.txt"]


def test_check_return_value_is_ignored(tmp_path, make_builder):
    make_builder().make_documents({"a.txt": {"name": "A"}}, check=lambda _n, _t: False)
    assert (tmp_path / "out" / "a.txt").read_text() == "A"


def test_listeners_get_the_configuration_context(make_builder):
    builder = make_builder()
    received = []
    builder.add_before_rendering_listener(received.append)
    builder.add_after_rendering_listener(received.append)
    builder.make_documents({"a.txt": {"name": "A"}})
    assert received == [builder.configuration_context, builder.configuration_context]
