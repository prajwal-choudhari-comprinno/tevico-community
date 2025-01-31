"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-1-31
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_password_policy_minimum_length_14(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        
        try:
            # Create an IAM client using the provided boto3 session
            client = connection.client('iam')
            
            # Fetch the account's IAM password policy
            account_password_policy = client.get_account_password_policy()
            password_policy = account_password_policy['PasswordPolicy']
            
            # Get the 'MinimumPasswordLength' setting from the password policy
            minimum_password_length = password_policy.get('MinimumPasswordLength', 0)

            # Check if 'MinimumPasswordLength' is 14 or more, indicating strong password policy
            report.status = minimum_password_length >= 14
            report.resource_ids_status['password_policy'] = minimum_password_length >= 14

        except client.exceptions.NoSuchEntityException:
            # Handle the case where no password policy is found
            report.status = ResourceStatus.FAILED
            report.resource_ids_status['password_policy'] = False
        except Exception:
            # Handle any other errors
            report.status = ResourceStatus.FAILED

        # Return the generated report
        return report