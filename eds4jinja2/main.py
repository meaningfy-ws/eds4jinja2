from eds4jinja2.builders.report_builder import ReportBuilder

if __name__ == "__main__":
    repBuilder = ReportBuilder("/home/laur/work/eds4jinja2/tests/test_data/templates_test")
    repBuilder.make_document()