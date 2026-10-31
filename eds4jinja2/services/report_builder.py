#!/usr/bin/python3

# report_generator
# Created:  08/03/2019
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

"""
this module implements the report generation functionality.
"""

import json
import logging
import pathlib
from collections.abc import Callable, Mapping
from typing import Any, TypeVar

import jinja2

from eds4jinja2.models.collections import deep_update
from eds4jinja2.services.jinja_builder import (
    ADDITIONAL_FILTERS,
    DATA_SOURCE_BUILDERS,
    TABULAR_HELPERS,
    TREE_HELPERS,
    build_eds_environment,
    inject_environment_globals,
)
from eds4jinja2.services.parallel_executor import DEFAULT_PARALLELISM, PARALLELISM, FetchCoordinator, Phase, wrap_builders

logger = logging.getLogger(__name__)

T = TypeVar("T")

# aims to be close to the J2 default env syntax definition, but explicitly specified
HTML_TEMPLATE_SYNTAX = {
    "block_start_string": "{%",
    "block_end_string": "%}",
    "variable_start_string": "{{",
    "variable_end_string": "}}",
    "comment_start_string": "{#",
    "comment_end_string": "#}",
    "line_statement_prefix": "#",
    "line_comment_prefix": "##",
    "trim_blocks": False,
}

# do not change anything
DEFAULT_TEMPLATE_SYNTAX: dict = {}

######################################################################
# Jinja2 Environment ARGS
#   Constant borrowed from Marc Brinkmann's latex repository (mbr/latex on github)
#   Reused also by Samuel Roeca's in his latex repository (pappasam/latexbuild on github)
######################################################################
LATEX_TEMPLATE_SYNTAX = {
    "block_start_string": r"\BLOCK{",
    "block_end_string": "}",
    "variable_start_string": r"\VAR{",
    "variable_end_string": "}",
    "comment_start_string": r"\#{",
    "comment_end_string": "}",
    "line_statement_prefix": "%-",
    "line_comment_prefix": "%#",
    "trim_blocks": True,
    "autoescape": False,
}


class ReportBuilder:
    """
    generic report builder that takes templates and configuration as input and produces an output report
    """

    configuration_context: dict = {}

    def __init__(
        self,
        target_path: str | pathlib.Path,
        config_file: str = "config.json",
        output_path: str | None = None,
        additional_config: dict | None = None,
        external_data_source_builders: dict | None = None,
        external_filters: dict | None = None,
    ):
        """
            Instantiates builders form a template providing an optional configuration context.

        :type additional_config: additional config parameters that are added to the default
                                ones be overwritten (deep update) in the project config.json
        :param target_path: the folder where the required resources are found
        :param config_file: the configuration file (default 'config.json')
        :param output_path: the output folder where the result of the rendering will be created
        :param external_data_source_builders: additional/overriding data-source builders made
                                available to templates; merged *over* the framework defaults, so a
                                consumer can e.g. override ``from_endpoint`` to serve an in-memory
                                graph. Empty/None reproduces the default behaviour exactly.
        :param external_filters: additional/overriding Jinja filters, merged over the defaults.
        """

        with open(pathlib.Path(target_path) / config_file, encoding="utf-8") as configFile:
            self.configuration_context = json.loads(configFile.read())
        deep_update(self.configuration_context, additional_config or {})

        template_path = str(pathlib.Path(target_path) / "templates")
        static_folder = pathlib.Path(target_path) / "static"
        if output_path is not None:
            output_folder = pathlib.Path(output_path)
        else:
            # in case you don't specify an output, the rendered content will be placed
            # in the target folder, in an default directory named "output"
            # this is to prevent creating files wherever you happen to run the CLI
            output_folder = pathlib.Path(target_path) / "output"

        self.configuration_context["template_path"] = template_path
        self.configuration_context["static_folder"] = str(static_folder)
        self.configuration_context["output_folder"] = str(output_folder)
        self.configuration_context["conf"]["template_path"] = template_path
        self.template = self.configuration_context["template"]

        # Provides a configuration of the templating syntax flavour. By default it is configured
        # for HTML but could be adapted as necessary. For LaTex, LATEX_TEMPLATE_SYNTAX is available.
        # TODO: this code might need to be externalised in the next refactoring
        if "template_flavour_syntax" in self.configuration_context:
            if str.lower(self.configuration_context["template_flavour_syntax"]) in ("latex", "tex"):
                self.template_flavour_syntax_spec = LATEX_TEMPLATE_SYNTAX
            elif str.lower(self.configuration_context["template_flavour_syntax"]) in ("xml", "html", "xhtml"):
                self.template_flavour_syntax_spec = HTML_TEMPLATE_SYNTAX
            else:
                self.template_flavour_syntax_spec = DEFAULT_TEMPLATE_SYNTAX
        else:
            self.template_flavour_syntax_spec = DEFAULT_TEMPLATE_SYNTAX

        # Merge any injected builders/filters OVER the framework defaults. build_eds_environment
        # *replaces* its registries with whatever it receives, so forwarding a partial dict would
        # silently drop the default helpers (from_file, invert_dict, escape_latex, ...). Merging
        # preserves them while letting an injected entry (e.g. from_endpoint) override its default.
        data_source_builders = {
            **DATA_SOURCE_BUILDERS,
            **TABULAR_HELPERS,
            **TREE_HELPERS,
            **(external_data_source_builders or {}),
        }
        filters = {**ADDITIONAL_FILTERS, **(external_filters or {})}

        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        self.template_env = build_eds_environment(
            loader=template_loader,
            external_data_source_builders=data_source_builders,
            external_filters=filters,
            **self.template_flavour_syntax_spec,
        )
        inject_environment_globals(
            self.template_env,
            {"conf": self.configuration_context["conf"]},
            False if self.configuration_context is None else True,
        )

        self.__before_rendering_listeners: list = []
        self.__after_rendering_listeners: list = []

    def add_before_rendering_listener(self, listener):
        """
        At the moment there is no use for this.
        """
        self.__before_rendering_listeners.append(listener)

    def add_after_rendering_listener(self, listener):
        """
        At the moment, this is used just to copy static files to the output directory.
        For example, CSS, JavaScript and other static resources.
        """
        self.__after_rendering_listeners.append(listener)

    def __get_template(self, template_name=None) -> jinja2.Template:
        """
            Standard JINJA2 get_template() functionality.
        :param template_name:
        :return:
        """
        if not template_name:
            return self.template_env.get_template(self.template)
        else:
            return self.template_env.get_template(template_name)

    def make_document(self):
        """
        Render the report. Sequential by default; when the config sets ``parallelism`` > 1
        the data fetches are pre-warmed in parallel (see ``parallel_executor``). With
        ``parallelism`` unset or 1 the behaviour is byte-for-byte the previous sequential path.
        """
        parallelism = self.__parallelism()
        if parallelism > 1:
            self.__with_prefetch(parallelism, {}, self.__render_to_output)
        else:
            self.__render_to_output()

    def render_documents(self, outputs: Mapping[str, Mapping[str, Any]], *, autoescape: bool | None = None) -> dict[str, str]:
        """
        Render the configured template once per output, in memory, and return output name -> text
        in the order of ``outputs``. Writes no file and runs no rendering listener.

        :param outputs: output name (a relative path inside the output folder) -> template variables
        :param autoescape: when given, the environment's autoescaping for this batch only
        :raises ValueError: a name outside the output folder, or a variable named ``conf``
                            (the configuration stays the ``conf`` global); raised before any render
        """
        self.__output_paths(outputs)
        previous_autoescape = self.template_env.autoescape
        switch = autoescape is not None and autoescape != previous_autoescape
        if switch:
            self.__set_autoescape(autoescape)
        try:
            return {name: self.__render_text(variables) for name, variables in outputs.items()}
        finally:
            if switch:
                self.__set_autoescape(previous_autoescape)

    def make_documents(
        self,
        outputs: Mapping[str, Mapping[str, Any]],
        *,
        check: Callable[[str, str], None] | None = None,
        autoescape: bool | None = None,
    ) -> list[pathlib.Path]:
        """
        Render every output as ``render_documents`` does, call ``check(name, text)`` on each, and
        only when every check returns write every text as UTF-8 under the output folder (creating
        sub-folders). Return the written paths in the order of ``outputs``.

        The before-rendering listeners run once before the batch, the after-rendering listeners once
        after the files are written; neither runs for an empty batch or a refused name/variable,
        and the after-rendering listeners do not run when rendering or a check fails.

        :param check: refuses an output by raising; the exception propagates unchanged and no file
                      is written. Writes are not atomic: a disk error mid-batch can leave some files.
        :raises ValueError: as ``render_documents``, before any listener runs
        """
        if not outputs:
            return []
        paths = self.__output_paths(outputs)

        for listener in self.__before_rendering_listeners:
            listener(self.configuration_context)

        texts = self.render_documents(outputs, autoescape=autoescape)
        if check is not None:
            for name, text in texts.items():
                check(name, text)
        for path, text in zip(paths, texts.values(), strict=True):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

        for listener in self.__after_rendering_listeners:
            listener(self.configuration_context)
        return paths

    def __output_paths(self, outputs: Mapping[str, Mapping[str, Any]]) -> list[pathlib.Path]:
        """Validate a batch before anything is rendered; return its output paths in order."""
        for name, variables in outputs.items():
            if "conf" in variables:
                raise ValueError(f"output {name!r}: the template variable 'conf' is reserved for the configuration")
        return [self.__output_path(name) for name in outputs]

    def __set_autoescape(self, autoescape) -> None:
        # Jinja compiles autoescaping into the cached template, so drop the cache with the setting
        self.template_env.autoescape = autoescape
        if self.template_env.cache is not None:
            self.template_env.cache.clear()

    def __render_text(self, variables: Mapping[str, Any]) -> str:
        def render() -> str:
            return self.__get_template(self.template).render(**variables)

        parallelism = self.__parallelism()
        return self.__with_prefetch(parallelism, variables, render) if parallelism > 1 else render()

    def __output_path(self, name: str) -> pathlib.Path:
        """The path of output ``name``; it must lie inside the output folder and differ from it."""
        folder = pathlib.Path(self.configuration_context["output_folder"]).resolve()
        path = (folder / name).resolve()
        if folder not in path.parents:
            raise ValueError(f"output {name!r} is not a file name inside the output folder {str(folder)!r}")
        return path

    def __parallelism(self) -> int:
        return int(self.configuration_context.get(PARALLELISM, DEFAULT_PARALLELISM) or DEFAULT_PARALLELISM)

    def __render_to_output(self):
        for listener in self.__before_rendering_listeners:
            listener(self.configuration_context)

        template = self.__get_template(self.template)

        pathlib.Path(self.configuration_context["output_folder"]).mkdir(parents=True, exist_ok=True)
        template.stream().dump(str(pathlib.Path(self.configuration_context["output_folder"]) / self.template))

        for listener in self.__after_rendering_listeners:
            listener(self.configuration_context)

    def __with_prefetch(self, parallelism: int, variables: Mapping[str, Any], render: Callable[[], T]) -> T:
        """Run ``render`` with the data fetches pre-warmed in parallel; ``variables`` drive the record pass."""
        coordinator = FetchCoordinator()
        original_globals = dict(self.template_env.globals)
        try:
            self.template_env.globals.update(wrap_builders(self.template_env.globals, set(DATA_SOURCE_BUILDERS), coordinator))

            # Record pass: discover the fetch units. If it fails (e.g. a data-dependent template
            # chokes on placeholder results) we fall back to a normal sequential render.
            coordinator.set_phase(Phase.RECORD)
            try:
                self.__get_template(self.template).render(**variables)
            except Exception as record_error:
                logger.warning("Parallel record pass failed (%s); rendering sequentially", record_error)
                self.__restore_globals(original_globals)
                return render()

            # Pre-warm in parallel — all-or-nothing: a failure here aborts the whole report.
            coordinator.prewarm(parallelism)

            # Real render: fetches are served from the cache (misses run live).
            coordinator.set_phase(Phase.RENDER)
            return render()
        finally:
            coordinator.cleanup()
            self.__restore_globals(original_globals)

    def __restore_globals(self, original_globals: dict):
        self.template_env.globals.clear()
        self.template_env.globals.update(original_globals)
