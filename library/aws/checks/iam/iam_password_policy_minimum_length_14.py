"""
AUTHOR: SUPRIYO BHAKAT
DATE: 10/10/2024
"""

import boto3
from botocore.exceptions import ClientError

from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check


class iam_password_policy_minimum_length_14(Check):
    
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')

        # Attempt to retrieve the password policy
        try:
            password_policy = client.get_account_password_policy()
            policy_exists = True
        except ClientError as e:
            # Handle specific errors related to the IAM policy retrieval
            if e.response['Error']['Code'] == 'NoSuchEntity':
                print("No IAM password policy found.")
                policy_exists = False
            else:
                print(f"Unexpected error: {e}")  # Log unexpected errors
                policy_exists = False  # Default to no policy if an unexpected error occurs
        
        if policy_exists:
            # Check the length of the password policy
            password_policy_length = password_policy['PasswordPolicy'].get('MinimumPasswordLength', 0)
            if password_policy_length >= 14:
                report.passed = True
            else:
                report.passed = False
        else:
            report.passed = False

        # Report the status for the password policy check
        report.resource_ids_status['IAM Password Policy'] = report.passed
        return report
