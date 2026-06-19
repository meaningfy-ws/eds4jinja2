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
from typing import Union

import jinja2

from eds4jinja2.models.collections import deep_update
from eds4jinja2.services.jinja_builder import (build_eds_environment, inject_environment_globals,
                                               DATA_SOURCE_BUILDERS, TABULAR_HELPERS, TREE_HELPERS,
                                               ADDITIONAL_FILTERS)
from eds4jinja2.services.parallel_executor import (FetchCoordinator, Phase, wrap_builders,
                                                   PARALLELISM, DEFAULT_PARALLELISM)

logger = logging.getLogger(__name__)

# aims to be close to the J2 default env syntax definition, but explicitly specified
HTML_TEMPLATE_SYNTAX = {'block_start_string': '{%',
                        'block_end_string': '%}',
                        'variable_start_string': '{{',
                        'variable_end_string': '}}',
                        'comment_start_string': '{#',
                        'comment_end_string': '#}',
                        'line_statement_prefix': '#',
                        'line_comment_prefix': '##',
                        'trim_blocks': False, }

# do not change anything
DEFAULT_TEMPLATE_SYNTAX = {}

######################################################################
# Jinja2 Environment ARGS
#   Constant borrowed from Marc Brinkmann's latex repository (mbr/latex on github)
#   Reused also by Samuel Roeca's in his latex repository (pappasam/latexbuild on github)
######################################################################
LATEX_TEMPLATE_SYNTAX = {'block_start_string': r'\BLOCK{',
                         'block_end_string': '}',
                         'variable_start_string': r'\VAR{',
                         'variable_end_string': '}',
                         'comment_start_string': r'\#{',
                         'comment_end_string': '}',
                         'line_statement_prefix': '%-',
                         'line_comment_prefix': '%#',
                         'trim_blocks': True,
                         'autoescape': False, }


class ReportBuilder:
    """
        generic report builder that takes templates and configuration as input and produces an output report
    """
    configuration_context: dict = {}

    def __init__(self, target_path: Union[str, pathlib.Path], config_file: str = "config.json",
                 output_path: str = None, additional_config: dict = {},
                 external_data_source_builders: dict = None, external_filters: dict = None):
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

        with open(pathlib.Path(target_path) / config_file, encoding='utf-8') as configFile:
            self.configuration_context = json.loads(configFile.read())
        deep_update(self.configuration_context, additional_config)

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
        data_source_builders = {**DATA_SOURCE_BUILDERS, **TABULAR_HELPERS, **TREE_HELPERS,
                                **(external_data_source_builders or {})}
        filters = {**ADDITIONAL_FILTERS, **(external_filters or {})}

        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        self.template_env = build_eds_environment(loader=template_loader,
                                                  external_data_source_builders=data_source_builders,
                                                  external_filters=filters,
                                                  **self.template_flavour_syntax_spec)
        inject_environment_globals(self.template_env, {'conf': self.configuration_context["conf"]},
                                   False if self.configuration_context is None else True)

        self.__before_rendering_listeners = []
        self.__after_rendering_listeners = []

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
        parallelism = int(self.configuration_context.get(PARALLELISM, DEFAULT_PARALLELISM) or DEFAULT_PARALLELISM)
        if parallelism > 1:
            self.__make_document_parallel(parallelism)
        else:
            self.__render_to_output()

    def __render_to_output(self):
        for listener in self.__before_rendering_listeners:
            listener(self.configuration_context)

        template = self.__get_template(self.template)

        pathlib.Path(self.configuration_context["output_folder"]).mkdir(parents=True, exist_ok=True)
        template.stream().dump(str(pathlib.Path(self.configuration_context["output_folder"]) / self.template))

        for listener in self.__after_rendering_listeners:
            listener(self.configuration_context)

    def __make_document_parallel(self, parallelism: int):
        coordinator = FetchCoordinator()
        original_globals = dict(self.template_env.globals)
        try:
            self.template_env.globals.update(
                wrap_builders(self.template_env.globals, set(DATA_SOURCE_BUILDERS), coordinator))

            # Record pass: discover the fetch units. If it fails (e.g. a data-dependent template
            # chokes on placeholder results) we fall back to a normal sequential render.
            coordinator.set_phase(Phase.RECORD)
            try:
                self.__get_template(self.template).render()
            except Exception as record_error:
                logger.warning("Parallel record pass failed (%s); rendering sequentially", record_error)
                self.__restore_globals(original_globals)
                self.__render_to_output()
                return

            # Pre-warm in parallel — all-or-nothing: a failure here aborts the whole report.
            coordinator.prewarm(parallelism)

            # Real render: fetches are served from the cache (misses run live).
            coordinator.set_phase(Phase.RENDER)
            self.__render_to_output()
        finally:
            coordinator.cleanup()
            self.__restore_globals(original_globals)

    def __restore_globals(self, original_globals: dict):
        self.template_env.globals.clear()
        self.template_env.globals.update(original_globals)
