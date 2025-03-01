"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-14
"""

import boto3

from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, ResourceStatus, GeneralResource
from tevico.engine.entities.check.check import Check


class iam_user_multiple_active_access_keys(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            client = connection.client("iam")
            users = client.list_users()["Users"]

            for user in users:
                username = user["UserName"]
                arn = user["Arn"]  # IAM User ARN for proper resource tracking

                # Retrieve access keys for the user
                access_keys = client.list_access_keys(UserName=username)["AccessKeyMetadata"]

                # Count active access keys
                active_keys_count = sum(1 for key in access_keys if key["Status"] == "Active")

                # Define AwsResource
                resource = AwsResource(arn=arn)

                # Append the status of this user
                status = CheckStatus.PASSED if active_keys_count <= 1 else CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=resource,
                        status=status,
                        summary=f"Number of active access key(s) {active_keys_count}."
                    )
                )

        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=resource,
                    status=status,
                    summary=f"Error while checking access keys for IAM users.",
                    exception=str(e)
                )
            )

                        
        return report
