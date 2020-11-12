#!/usr/bin/python3

# report_generator
# Created:  08/03/2019
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

"""
this module implements the report generation functionality.
"""
import json
import pathlib
import jinja2

from eds4jinja2.builders import deep_update
from eds4jinja2.builders.jinja_builder import build_eds_environment, inject_environment_globals


class ReportBuilder:
    """
        generic report builder that takes templates and configuration as input and produces an output report
    """
    configuration_context: dict = {}

    def __init__(self, target_path, config_file="config.json",
                 output_path=None, additional_config: dict = {}, ):
        """
            Instantiates builders form a template providing an optional configuration context.

        :type additional_config: additional config parameters that are added to the default
                                ones be overwritten (deep update) in the project config.json
        :param target_path: the folder where the required resources are found
        :param config_file: the configuration file (default 'config.json')
        :param output_path: the output folder where the result of the rendering will be created
        """

        with open(pathlib.Path(target_path) / config_file, encoding='utf-8') as configFile:
            self.configuration_context = json.loads(configFile.read())

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

        deep_update(self.configuration_context, additional_config)
        self.template = self.configuration_context["template"]
        self.configuration_context = self.configuration_context

        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        self.template_env = build_eds_environment(loader=template_loader)
        self.configuration_context["conf"]["template_path"] = template_path
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
        for listener in self.__before_rendering_listeners:
            listener(self.configuration_context)

        template = self.__get_template(self.template)

        pathlib.Path(self.configuration_context["output_folder"]).mkdir(parents=True, exist_ok=True)
        template.stream().dump(str(pathlib.Path(self.configuration_context["output_folder"]) / self.template))

        for listener in self.__after_rendering_listeners:
            listener(self.configuration_context)
