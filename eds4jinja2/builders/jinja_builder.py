#!/usr/bin/python3
#
# jinja_builder
# Created:  18/03/2019
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

import jinja2

from eds4jinja2.adapters.local_sparql_ds import RDFFileDataSource
from eds4jinja2.adapters.tabular_utils import invert_dict, replace_strings_in_tabular, add_relative_figures
from eds4jinja2.adapters.file_ds import FileDataSource
from eds4jinja2.adapters.remote_sparql_ds import RemoteSPARQLEndpointDataSource

DATA_SOURCE_BUILDERS = {
    "from_endpoint": lambda endpoint: RemoteSPARQLEndpointDataSource(endpoint),
    "from_file": lambda file_path: FileDataSource(file_path),
    "from_rdf_file": lambda from_rdf_file: RDFFileDataSource(from_rdf_file)
}

TABULAR_HELPERS = {
    "invert_dict": lambda mapping_dict, reduce_values=True: invert_dict(mapping_dict, reduce_values),
    "replace_strings_in_tabular": lambda data_frame, target_columns, value_mapping_dict,
                                         mark_touched_rows=False: replace_strings_in_tabular(data_frame,
                                                                                             target_columns,
                                                                                             value_mapping_dict,
                                                                                             mark_touched_rows),
    "add_relative_figures": lambda data_frame, target_columns, relativisers,
                                   percentage=True: add_relative_figures(data_frame, target_columns, relativisers,
                                                                         percentage),
}


def build_eds_environment(external_data_source_builders={**DATA_SOURCE_BUILDERS, **TABULAR_HELPERS}, **kwargs):
    """
        creates a JINJA environment and injects the global context with EDS functions
    :param external_data_source_builders:
    :param kwargs:
    :return:
    """
    template_env = jinja2.Environment(**kwargs)
    inject_environment_globals(template_env, external_data_source_builders)
    return template_env


def inject_environment_globals(jinja_environment: jinja2.Environment, context: dict, update_existent=True):
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
