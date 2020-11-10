#!/usr/bin/python3

# report_generator
# Created:  08/03/2019
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
"""This file contains the post-processing methods that you can use in conjunction with the ReportBuilder:

1. make_pdf_from_latex - allows you, after you rendered a ".tex" file from a template, to make a PDF file out of it

2.copy_static_content - it simply does what it says, copies resources from the static resources folder to the output
folder (for example, in case of a more complex rendered HTML, you will need this to copy .css, .js and other files);
the input directory structure is preserved to the output folder during copying

"""
import glob
import logging
import os
import pathlib
from distutils.dir_util import copy_tree
from subprocess import Popen, PIPE

__logger = logging.getLogger(__name__)


def make_pdf_from_latex(static_folder, output_folder, configuration_context) -> None:
    """
    :rtype: None
    :param static_folder: this is the static resources folder, in case you need to copy something from there to the output folder
    :param output_folder: this is the output folder where the output of the template renderer will be placed
    :param configuration_context: the configuration context of the renderer; in this method it is used to construct the output PDF file name

    """
    input_file_name = pathlib.Path(output_folder) / configuration_context["template"]
    output_pdf_file = input_file_name.with_suffix(".pdf")
    process = Popen(
        ["pdflatex", "-file-line-error", "-interaction=nonstopmode", "-synctex=1",
         "-output-format=pdf", "-output-directory=" + output_folder, input_file_name],
        stdout=PIPE)
    output, _ = process.communicate()

    if process.returncode != 0:
        __logger.fatal('pdflatex execution failed.')
        __logger.fatal(f'OUTPUT: {output.decode()}')
        raise RuntimeError(output)

    __logger.info('Subprocess finished successfully.')
    __logger.info(output.decode())

    file_list = glob.glob(output_folder + "/*.*")
    for file in file_list:
        try:
            if file != str(output_pdf_file):
                os.remove(file)
        except Exception:
            __logger.exception("Error while deleting file : " + file)


def copy_static_content(from_path, to_path, configuration_context) -> None:
    """
    :rtype: None
    :param from_path: the static resources folder (may contain all sorts of files, such as .css, .js, etc.)
    :param to_path: the rendered output folder (typically, here you will find, for example, the output HTML)
    """
    if pathlib.Path(from_path).is_dir():
        copy_tree(from_path, to_path)
    else:
        __logger.warning(from_path + " is not a directory !")
