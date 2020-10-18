import pathlib
from distutils.dir_util import copy_tree
from eds4jinja2.builders.report_builder import ReportBuilder
import click
import logging

__logger = logging.getLogger(__name__)


def copy_static_content(from_path, to_path):
    if pathlib.Path(from_path).is_dir():
        copy_tree(from_path, to_path)
    else:
        __logger.warning(from_path + " is not a directory !")


@click.command()
@click.option("--target", required=True, type=str, help="The folder containing the config.json")
@click.option("--config", default="config.json", type=str,
              help="The configuration file if named other than config.json")
@click.option("--output", required=False, type=str, help="The output folder")
def build_report(target, config, output):
    report_builder = ReportBuilder(target_path=target, config_file=config, output_path=output)
    report_builder.add_after_rendering_listener(copy_static_content)
    report_builder.make_document()


if __name__ == "__main__":
    build_report()
