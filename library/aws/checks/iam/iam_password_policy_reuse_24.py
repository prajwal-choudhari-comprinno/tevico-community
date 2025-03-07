"""
AUTHOR: Supriyo Bhakat <supriyo.bhakat@comprinno.net>
DATE: 2024-10-10
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_password_policy_reuse_24(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        
        try:
            client = connection.client('iam')
            account_password_policy = client.get_account_password_policy()
            password_policy = account_password_policy['PasswordPolicy']
            reuse_prevention = password_policy.get('PasswordReusePrevention', 0)
            
            status = CheckStatus.PASSED
            summary = f'Users are allowed to reuse the password after {reuse_prevention} password changes.'
            
            if reuse_prevention < 10:
                status = CheckStatus.FAILED
                summary = f'{summary} More than the threshold of 10 attempts.'

            report.status = status
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=status,
                    summary=summary
                )
            )

        except client.exceptions.NoSuchEntityException as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=CheckStatus.FAILED,
                    summary=f'No password reuse prevention policy set on this account.',
                    exception=str(e)
                )
            )
        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=CheckStatus.ERRORED,
                    summary=f'An unknown error occurred during the execution of this check.',
                    exception=str(e)
                )
            )
        return report
