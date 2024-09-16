import boto3

from tevico.app.entities.report.check_model import CheckReport
from tevico.app.entities.check.check import Check


class awslambda_function_invoke_api_operations_cloudtrail_logging_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        raise NotImplementedError
