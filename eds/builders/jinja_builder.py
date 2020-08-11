""" 
jinja_builder
Created:  18/03/2019
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com
"""
import jinja2

from eds.adapters.file_ds import FileDataSource
from eds.adapters.sparql_ds import SPARQLEndpointDataSource

FROM_ENDPOINT = "from_endpoint"
FROM_FILE = "from_file"

DATA_SOURCE_BUILDERS = {
    FROM_ENDPOINT: lambda endpoint: SPARQLEndpointDataSource(endpoint),
    FROM_FILE: lambda file_path: FileDataSource(file_path)
}


def get_eds_environment(external_data_source_builders=DATA_SOURCE_BUILDERS, **kwargs):
    """
        creates a JINJA environment and injects the global context with EDS functions
    :param external_data_source_builders:
    :param kwargs:
    :return:
    """
    template_env = jinja2.Environment(**kwargs)
    inject_environment_globals(template_env, external_data_source_builders)
    return template_env


class EDSEnvironment:
    """
        TODO: extend the environment class, be careful to update the the class dependency injections in the original code
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
        self.template_env = jinja2.Environment(loader=template_loader)
        inject_environment_globals(self.template_env, {'configuration', self.configuration_context})
        inject_environment_globals(self.template_env, DATA_SOURCE_BUILDERS)

    def get_template(self, template_name=None):
        """
            Standard JINA2 get_template() functionality.
        :param template_name: 
        :return:
        """
        if template_name:
            return self.template_env.get_template(self.main_template_name)
        else:
            self.template_env.get_template(template_name)

    def from_string(self, template_string):
        """
            Standard JINA2 from_string() functionality.
        :param template_string:
        :return:
        """
        self.template_env.from_string(template_string, globals=self.template_env.globals)


def inject_environment_globals(jinja_environment, context, update_existent=True):
    """
        Inject the context into JINJA2 environment making it globally available from any template.
        Update in place a dictionary by adding non existent keys from another dictionary.
        If the dictionary keys exist then they are replaced depending whether the update_existent flag is set.
    :param update_existent:
    :param context:
    :param jinja_environment:
    :return:
    """
    if update_existent:
        jinja_environment.globals.update(context)
    else:
        jinja_environment.globals.update(
            {k: v for k, v in context.items() if k not in jinja_environment.globals.keys()})
