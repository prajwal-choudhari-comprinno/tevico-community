"""
AUTHOR: Supriyo Bhakat <supriyo.bhakat@comprinno.net>
DATE: 2024-10-10
"""


import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_no_root_access_keys(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')

        try:
            response = client.list_access_keys()
            has_active_root_keys = any(
                access_key['Status'] == 'Active' for access_key in response['AccessKeyMetadata']
            )

            if has_active_root_keys:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name='root_account'),
                        status=CheckStatus.FAILED,
                        summary='',
                    )
                )
            else:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name='root_account'),
                        status=CheckStatus.PASSED,
                        summary='',
                    )
                )

            iam_users = client.list_users()['Users']

            for user in iam_users:
                user_name = user['UserName']
                response = client.list_access_keys(UserName=user_name)

                has_active_iam_keys = any(
                    access_key['Status'] == 'Active' for access_key in response['AccessKeyMetadata']
                )

                if has_active_iam_keys:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=user_name),
                            status=CheckStatus.FAILED,
                            summary=''
                        )
                    )
                else:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=user_name),
                            status=CheckStatus.PASSED,
                            summary=''
                        )
                    )

        except Exception:
            report.status = CheckStatus.FAILED

        return report
