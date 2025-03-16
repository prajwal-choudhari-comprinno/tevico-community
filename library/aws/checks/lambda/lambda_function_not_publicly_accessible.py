"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-14
"""

import boto3
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check
import json

class lambda_function_not_publicly_accessible(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('lambda')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED  # Default status
        report.resource_ids_status = []

        try:
            functions = client.list_functions().get('Functions', [])

            for function in functions:
                function_name = function['FunctionName']
                function_arn = function['FunctionArn']

                try:
                    policy_response = client.get_policy(FunctionName=function_name)
                    policy_json = policy_response.get('Policy', '{}')

                    # Parse policy JSON
                    policy_statements = json.loads(policy_json).get('Statement', [])

                    # Check for public access
                    is_public = any(
                        statement.get('Effect') == 'Allow' and
                        statement.get('Principal') == "*"
                        for statement in policy_statements
                    )

                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=function_arn),
                            status=CheckStatus.FAILED if is_public else CheckStatus.PASSED,
                            summary=f"Lambda function {function_name} is {'publicly accessible' if is_public else 'private'}."
                        )
                    )

                    if is_public:
                        report.status = CheckStatus.FAILED  # Mark overall report as FAILED if any function is public

                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    
                    if error_code == 'ResourceNotFoundException':
                        # Function has no policy, meaning it's private
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=function_arn),
                                status=CheckStatus.PASSED,
                                summary=f"Lambda function {function_name} has no policy, assumed private."
                            )
                        )
                    else:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=function_arn),
                                status=CheckStatus.FAILED,
                                summary=f"Failed to retrieve policy for {function_name}: {str(e)}"
                            )
                        )
                        report.status = CheckStatus.FAILED

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Unexpected error: {str(e)}"
                )
            )

        return report
