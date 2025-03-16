"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-1-31
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_password_policy_minimum_length_14(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        
        report.resource_ids_status = []
        
        report.status = CheckStatus.PASSED
        
        try:
            # Create an IAM client using the provided boto3 session
            client = connection.client('iam')
            
            # Fetch the account's IAM password policy
            account_password_policy = client.get_account_password_policy()
            password_policy = account_password_policy['PasswordPolicy']
            
            # Get the 'MinimumPasswordLength' setting from the password policy
            minimum_password_length = password_policy.get('MinimumPasswordLength', 0)
            
            status = CheckStatus.FAILED
            
            if minimum_password_length >= 14:
                status = CheckStatus.PASSED

            # Check if 'MinimumPasswordLength' is 14 or more, indicating strong password policy
            report.status = status
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=status,
                    summary='Password contains more than 14 characters.'
                )
            )

        except client.exceptions.NoSuchEntityException as e:
            # Handle the case where no password policy is found
            report.status = CheckStatus.ERRORED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=CheckStatus.ERRORED,
                    summary='No password policy found.',
                    exception=str(e)
                )
            )
        except Exception as e:
            # Handle any other errors
            report.status = CheckStatus.ERRORED
            
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='password_policy'),
                    status=CheckStatus.ERRORED,
                    summary='Unhandled exception occurred.',
                    exception=str(e)
                )
            )

        # Return the generated report
        return report