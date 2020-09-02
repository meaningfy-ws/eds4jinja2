#!/usr/bin/python3

# report_generator
# Created:  08/03/2019
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

"""
this module implements the report generation functionality.
"""
import jinja2

from eds4jinja2.builders.jinja_builder import build_eds_environment, inject_environment_globals


class ReportBuilder:
    """
        generic report builder that takes templates and configuration as input and produces an output report
    """

    def __init__(self, template_folder, main_template_name, configuration_context=None):
        """
            Instantiates builders form a template providing an optional configuration context.

        :param template_folder: the folder where JINJA2 templates are found
        :param main_template_name: the main builders template that will be used to generate the builders
        :param configuration_context: the configuration context available in the templates under the key "configuration"
        """
        self.main_template_name = main_template_name
        self.configuration_context = configuration_context

        template_loader = jinja2.FileSystemLoader(searchpath=str(template_folder))
        self.template_env = build_eds_environment(loader=template_loader)
        inject_environment_globals(self.template_env, {'configuration', self.configuration_context}, False if configuration_context is None else True)
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
            return self.template_env.get_template(self.main_template_name)
        else:
            self.template_env.get_template(template_name)

    # def __from_string(self, template_string) -> jinja2.Template:
    #     """
    #         Standard JINA2 from_string() functionality.
    #     :param template_string:
    #     :return:
    #     """
    #     self.template_env.from_string(template_string, globals=self.template_env.globals)

    def make_document(self) :
        for listener in self.__beforeRenderingListeners:
            listener()
        template = self.__get_template(self.main_template_name)

        template.stream().dump("~/output.html")
        #copy resources

        for listener in self.__afterRenderingListeners:
            listener()

