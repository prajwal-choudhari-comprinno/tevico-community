"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-14
"""

import boto3

from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, ResourceStatus, GeneralResource
from tevico.engine.entities.check.check import Check


class iam_user_mfa_enabled_console_access(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('iam')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            users = client.list_users().get('Users', [])

            if not users:
                report.status = CheckStatus.SKIPPED
                report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(resource=""),
                            status=CheckStatus.SKIPPED,
                            summary=f"No IAM users found."
                        )
                    )
                return report

            for user in users:
                username = user['UserName']
                arn = user['Arn']
                resource = AwsResource(arn=arn)

                # Check if the user has console access
                try:
                    client.get_login_profile(UserName=username)
                    
                except client.exceptions.NoSuchEntityException:
                    # User doesn't have console access, skip MFA check
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.SKIPPED,
                            summary="User {username} does not have console access."
                        )
                    )
                    continue
                except Exception as e:
                    report.report_metadata = {"error": str(e)}
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.ERRORED,
                            summary=f"Error checking console access.",
                            exception=e
                        )
                    )
                    report.status = CheckStatus.ERRORED
                    continue

                # Check if MFA is enabled for console-access users
                try:
                    mfa_response = client.list_mfa_devices(UserName=username)
                    mfa_devices = mfa_response.get('MFADevices', [])

                    if mfa_devices:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED,
                                summary="Console access is enabled with MFA configured."
                            )
                        )
                    else:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary="Console access is enabled, but MFA is not configured."
                            )
                        )
                        report.status = CheckStatus.FAILED

                except Exception as e:
                    report.report_metadata = {"error": str(e)}
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.ERRORED,
                            summary=f"Error checking MFA configuration.",
                            exception=e
                        )
                    )
                    report.status = CheckStatus.ERRORED

        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=resource,
                    status=CheckStatus.ERRORED,
                    summary=f"Error while checking MFA for IAM users",
                    exception=e
                )
            )

        return report
