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
            users = client.list_users()['Users']

            for user in users:
                username = user['UserName']
                arn = user['Arn']
                resource = AwsResource(arn=arn)
                
                # First check if user has console access
                try:
                    # get_login_profile raises NoSuchEntity if user has no console access
                    client.get_login_profile(UserName=username)
                    has_console_access = True
                except client.exceptions.NoSuchEntityException:
                    # User doesn't have console access, skip MFA check
                    report.resource_ids_status.append(
                        ResourceStatus(resource=resource, 
                                       status=CheckStatus.PASSED, 
                                       summary=f"Console access is not enabled."
                                    )
                    )
                    continue
                except Exception as e:
                    report.report_metadata = {f"Error checking login profile for user {username}": str(e)}
                    continue

                # Only check MFA if user has console access
                if has_console_access:
                    response = client.list_mfa_devices(UserName=username)
                    mfa_devices = response['MFADevices']

                    if mfa_devices:
                        for mfa_device in mfa_devices:
                            if mfa_device['EnableDate']:
                                report.resource_ids_status.append(
                                    ResourceStatus(resource=resource, status=CheckStatus.PASSED, summary=f"Console access is enabled with MFA configured.")
                                )
                    else:
                        report.resource_ids_status.append(
                            ResourceStatus(resource=resource, status=CheckStatus.FAILED, summary=f"Console access is enabled, but MFA is not configured.")
                        )
                        report.status = CheckStatus.FAILED

        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}

        return report