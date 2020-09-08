#!/usr/bin/python3

# report_generator
# Created:  08/03/2019
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

"""
this module implements the report generation functionality.
"""
import json
import pathlib

import jinja2

from eds4jinja2 import FileDataSource, SPARQLEndpointDataSource
from eds4jinja2.builders.jinja_builder import build_eds_environment, inject_environment_globals


class ReportBuilder:
    """
        generic report builder that takes templates and configuration as input and produces an output report
    """
    __STATIC_FOLDER__ = "static"
    __TEMPLATE_FOLDER__ = "templates"
    __DEFAULT_CONFIG_FILE__ = "config.json"
    __DEFAULT_OUTPUT_DIRECTORY__ = "output"

    def __init__(self, input_folder, config_file=__DEFAULT_CONFIG_FILE__, output_folder=__DEFAULT_OUTPUT_DIRECTORY__):
        """
            Instantiates builders form a template providing an optional configuration context.

        :param template_folder: the folder where JINJA2 templates are found
        :param main_template_name: the main builders template that will be used to generate the builders
        :param configuration_context: the configuration context available in the templates under the key "configuration"
        """

        with open(pathlib.Path(input_folder) / config_file, encoding='utf-8') as configFile:
            configuration_context = json.loads(configFile.read())

        self.template = configuration_context["template"]
        self.configuration_context = configuration_context
        self.__DEFAULT_OUTPUT_DIRECTORY__ = output_folder

        template_loader = jinja2.FileSystemLoader(searchpath=str(pathlib.Path(input_folder) / self.__TEMPLATE_FOLDER__))
        self.template_env = build_eds_environment(loader=template_loader)
        inject_environment_globals(self.template_env, {'conf': self.configuration_context["conf"]},
                                   False if configuration_context is None else True)
        self.__beforeRenderingListeners = []
        self.__afterRenderingListeners = []

    def addBeforeRenderingListener(self, listener):
        self.__beforeRenderingListeners.append(listener)

    def addAfterRenderingListener(self, listener):
        self.__afterRenderingListeners.append(listener)

    def __get_template(self, template_name=None) -> jinja2.Template:
        """
            Standard JINA2 get_template() functionality.
        :param template_name:
        :return:
        """
        if not template_name:
            return self.template_env.get_template(self.template)
        else:
            return self.template_env.get_template(template_name)

    # def __from_string(self, template_string) -> jinja2.Template:
    #     """
    #         Standard JINA2 from_string() functionality.
    #     :param template_string:
    #     :return:
    #     """
    #     self.template_env.from_string(template_string, globals=self.template_env.globals)

    def make_document(self):
        for listener in self.__beforeRenderingListeners:
            listener()

        template = self.__get_template(self.template)

        template.stream().dump("output.html")
        # copy resources - perhaps this is best to be done by an after rendering method that should be registered
        # by the consumer of this class

        for listener in self.__afterRenderingListeners:
            listener()
