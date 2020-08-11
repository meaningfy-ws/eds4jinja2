""" 
jinja_builder
Created:  18/03/2019
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""
import jinja2

from eds.adapters.file_ds import TreeFileDataSource
from eds.adapters.sparql_ds import SPARQLSelectDataSource, SPARQLDescribeDataSource
from eds.builders.report_builder import ReportBuilder

DATA_SOURCE_BUILDERS = {
    "from_select_endpoint": lambda query_string, endpoint: SPARQLSelectDataSource(query_string, endpoint),
    "from_describe_endpoint": lambda uri_string, endpoint: SPARQLDescribeDataSource(uri_string, endpoint),
    "from_tabular_file": lambda file_path: SPARQLDescribeDataSource(file_path),
    "from_tree_file": lambda file_path: TreeFileDataSource(file_path),
}


class JinjaBuilder(ReportBuilder):

    def __init__(self, template_folder, main_template_name, configuration_context=None, ):
        """
            Builds a builders form a template providing an optional configuration context.

        :param template_folder: the folder where JINJA2 templates are found
        :param main_template_name: the main builders template that will be used to generate the builders
        :param configuration_context: the configuration context available in the templates under the key "configuration"
        """
        self.main_template_name = main_template_name
        # self.configuration_context = configuration_context

        template_loader = jinja2.FileSystemLoader(searchpath=str(template_folder))
        self.template_env = jinja2.Environment(loader=self.template_loader)
        inject_globals(self.template_env, {'configuration', configuration_context})
        inject_globals(self.template_env, DATA_SOURCE_BUILDERS)
        # self.document_template = self.template_env.get_template(main_template_name)

    def get_template(self, template_name=None):
        """
            Standard JINA2 get_template() functionality.
        :param template_name: 
        :return:
        """
        if template_name:
            return self.template_env.get_template(self.main_template_name)
        else:
            self.template_env.get_template(self.main_template_name)

    def from_string(self, template_string):
        """
            Standard JINA2 from_string() functionality.
        :param template_string:
        :return:
        """
        self.template_env.from_string(template_string, globals=self.template_env.globals)

    def make_document(self):
        # return self.get_template().render()
        raise NotImplementedError


def inject_globals(context, jinja_environment):
    """
        inject the context into JINJA2 environment making it globally available from any template
    :param context:
    :param jinja_environment:
    :return:
    """
    controlled_injection(jinja2.globals, context)


def controlled_injection(inplace_dict, another_dict, update_existent=False):
    """
        Update in place a dictionary by adding non existent keys from another dictionary.
        If the dictionary keys exist then they are replaced depending whether the update_existent flag is set.
    :param update_existent:
    :param inplace_dict:
    :param another_dict:
    :return:
    """
    raise NotImplementedError
