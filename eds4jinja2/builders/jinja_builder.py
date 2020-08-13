#!/usr/bin/python3
#
# jinja_builder
# Created:  18/03/2019
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

import jinja2

from eds4jinja2.adapters.file_ds import FileDataSource
from eds4jinja2.adapters.sparql_ds import SPARQLEndpointDataSource

FROM_ENDPOINT = "from_endpoint"
FROM_FILE = "from_file"

DATA_SOURCE_BUILDERS = {
    FROM_ENDPOINT: lambda endpoint: SPARQLEndpointDataSource(endpoint),
    FROM_FILE: lambda file_path: FileDataSource(file_path)
}


def build_eds_environment(external_data_source_builders=DATA_SOURCE_BUILDERS, **kwargs):
    """
        creates a JINJA environment and injects the global context with EDS functions
    :param external_data_source_builders:
    :param kwargs:
    :return:
    """
    template_env = jinja2.Environment(**kwargs)
    inject_environment_globals(template_env, external_data_source_builders)
    return template_env


def inject_environment_globals(jinja_environment, context, update_existent=True):
    """
        Inject the context into JINJA2 environment making it globally available from any template.
        Update in place a dictionary by adding non existent keys from another dictionary.
        If the dictionary keys exist then they are replaced depending whether the update_existent flag is set.
    :param update_existent: whether the overlapping values shall be overwritten
    :param context: additional context to be injected
    :param jinja_environment: JINJA environment to be updated
    :return:
    """
    if update_existent:
        jinja_environment.globals.update(context)
    else:
        jinja_environment.globals.update(
            {k: v for k, v in context.items() if k not in jinja_environment.globals.keys()})


class EDSEnvironment:
    """
        TODO: extend the environment class, be careful to update the the class dependency injections in the original code
        TODO: this is possibly a cleaner alternative to  get_eds_environment, low priority
    """
