"""
AUTHOR: Mohd Asif <mohd.asif@comprinno.net>
DATE: 2024-10-10
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class iam_user_multiple_active_access_keys(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')
        try:
            # List all IAM users
            users = client.list_users()['Users']
            for user in users:
                username = user['UserName']
                # List access keys for each user
                access_keys = client.list_access_keys(UserName=username)['AccessKeyMetadata']
                active_keys_count = sum(1 for key in access_keys if key['Status'] == 'Active')
                
                if active_keys_count > 1:
                    # print(f"Multiple active access keys found for user: {username}")
                    report.resource_ids_status[username] = True
                else:
                    # print(f"User {username} has {active_keys_count} active access key(s).")
                    report.resource_ids_status[username] = False
            
            report.passed = not any(report.resource_ids_status.values())
        except Exception as e:
            # print("Error in checking multiple active access keys for users")
            # print(str(e))  # Log the error in the resource status
            report.passed = False
        return report
