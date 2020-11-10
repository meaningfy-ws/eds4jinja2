import logging
import click

from eds4jinja2.builders.report_builder import ReportBuilder
from eds4jinja2.builders.report_builder_actions import copy_static_content, make_pdf_from_latex

__logger = logging.getLogger(__name__)


@click.command()
@click.option("--target", required=True, type=str, help="The folder containing the config.json")
@click.option("--config", default="config.json", type=str,
              help="The configuration file if named other than config.json")
@click.option("--output", required=False, type=str, help="The output folder")
@click.option("--latex", is_flag=True, help="If this parameter is specified, the input will be treated as "
                                                        "a LaTeX template and the output will be rendered to PDF")
def build_report(target, config, output, latex):
    report_builder = ReportBuilder(target_path=target, config_file=config, output_path=output)
    if latex:
        report_builder.add_after_rendering_listener(make_pdf_from_latex)
    else:
        report_builder.add_after_rendering_listener(copy_static_content)
    report_builder.make_document()


if __name__ == "__main__":
    build_report()
