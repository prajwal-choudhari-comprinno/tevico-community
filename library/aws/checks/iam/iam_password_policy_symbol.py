"""
AUTHOR: Supriyo Bhakat <supriyo.bhakat@comprinno.net>
DATE: 2024-10-10
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_password_policy_symbol(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)

        try:
            client = connection.client('iam')
            account_password_policy = client.get_account_password_policy()
            password_policy = account_password_policy['PasswordPolicy']
            symbols_required = password_policy.get('RequireSymbols', False)
            
            status = CheckStatus.PASSED
            summary = f'IAM password policies contains a policy to have a symbol in the password.'
            
            if not symbols_required:
                status = CheckStatus.FAILED
                summary = f'IAM password policies does not contain a policy to have a symbol in the password.'
            
            report.status = status
            report.resource_ids_status.append(
                ResourceStatus(
                    status=status,
                    resource=GeneralResource(name='password_policy'),
                    summary=summary
                )
            )
        except client.exceptions.NoSuchEntityException as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    status=CheckStatus.ERRORED,
                    resource=GeneralResource(name='password_policy'),
                    summary=f'No such entity exception occurred during the execution of this check.',
                    exception=str(e)
                )
            )
        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.resource_ids_status.append(
                ResourceStatus(
                    status=CheckStatus.ERRORED,
                    resource=GeneralResource(name='password_policy'),
                    summary=f'An unknown error occurred during the execution of this check.',
                    exception=str(e)
                )
            )

        return report