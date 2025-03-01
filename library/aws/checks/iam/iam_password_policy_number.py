"""
AUTHOR: Supriyo Bhakat <supriyo.bhakat@comprinno.net>
DATE: 2024-10-10
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_password_policy_number(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.resource_ids_status = []
        try:
            client = connection.client('iam')
            account_password_policy = client.get_account_password_policy()
            password_policy = account_password_policy['PasswordPolicy']
            requires_number = password_policy.get('RequireNumbers', False)
            
            status = CheckStatus.PASSED
            summary = 'Password contains a number as a good practice.'
            
            if requires_number:
                status = CheckStatus.FAILED
                summary = 'Password does not contain a number as a good practice.'

            report.status = status
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=status,
                    summary=summary
                )
            )

        except client.exceptions.NoSuchEntityException as e:
            report.status = CheckStatus.ERRORED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=CheckStatus.ERRORED,
                    summary='No such entity exception was found during the execution of this check.',
                    exception=str(e)
                )
            )
        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=CheckStatus.ERRORED,
                    summary='An unknown error occurred during the execution of this check.',
                    exception=str(e)
                )
            )

        return report
