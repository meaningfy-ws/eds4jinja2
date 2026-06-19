"""
test_logging.py

The library must follow the standard logging idiom: importing eds4jinja2 must NOT configure the
root logger or attach an emitting handler — only a NullHandler on the package logger. Logging
configuration is the application's / entrypoint's job.
"""
import logging

import eds4jinja2  # noqa: F401  (import side-effects are what we assert on)


def test_package_logger_has_only_a_null_handler():
    handlers = logging.getLogger("eds4jinja2").handlers
    assert handlers, "expected a NullHandler on the eds4jinja2 package logger"
    assert all(isinstance(h, logging.NullHandler) for h in handlers), \
        "the library must not attach an emitting handler"


def test_import_does_not_force_root_logger_level():
    # importing the library must not pin the root logger to a fixed level (it left it default 0/WARNING)
    # we only assert the library did not set it to INFO as the old root-logger hijack did
    assert logging.getLogger("eds4jinja2").level == logging.NOTSET
