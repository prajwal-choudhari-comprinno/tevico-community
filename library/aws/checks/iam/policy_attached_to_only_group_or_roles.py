"""
AUTHOR: Mohd Asif
DATE: 11 oct 2024
"""


import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class policy_attached_to_only_group_or_roles(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')

        try:
            # List all IAM users
            users = client.list_users()['Users']

            # Check for attached policies for each user
            for user in users:
                username = user['UserName']
                # List attached user policies
                attached_policies = client.list_attached_user_policies(UserName=username)['AttachedPolicies']

                if attached_policies:
                    print(f"User {username} has policies attached directly.")
                    report.resource_ids_status[username] = True  # Flag as a violation
                else:
                    print(f"User {username} does not have any directly attached policies.")
                    report.resource_ids_status[username] = False  # No violation

            # Overall check passes if no user has directly attached policies
            report.passed = not any(report.resource_ids_status.values())

        except Exception as e:
            print("Error in checking policies attached directly to users")
            print(str(e))  # Log the error in the resource status
            report.passed = False

        return report

