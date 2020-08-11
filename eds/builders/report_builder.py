""" 
report_generator
Created:  08/03/2019
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com

this module implements the report generation functionality.
"""


class ReportBuilder:
    """
        generic report builder that takes templates and configuration as input and produces an output report
    """

    def make_document(self):
        raise NotImplementedError
