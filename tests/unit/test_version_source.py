"""
test_version_source.py

The package version has a single source of truth: the eds4jinja2/VERSION file. __version__ must
read from it (no hand-edited literal in code).
"""
import pathlib

import eds4jinja2


def test_version_matches_version_file():
    version_file = pathlib.Path(eds4jinja2.__file__).parent / "VERSION"
    assert eds4jinja2.__version__ == version_file.read_text(encoding="utf-8").strip()
    assert eds4jinja2.__version__  # non-empty
