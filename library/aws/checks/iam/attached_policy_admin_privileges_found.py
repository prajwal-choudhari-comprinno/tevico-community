"""
AUTHOR: RONIT CHAUHAN
DATE: 11-10-24
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class attached_policy_admin_privileges_found(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)

        # Initialize the IAM client
        iam_client = connection.client('iam')

        # Fetch all users and their attached policies
        users = iam_client.list_users()['Users']
        findings = []

        for user in users:
            user_name = user['UserName']
            policies = iam_client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']

            for policy in policies:
                policy_arn = policy['PolicyArn']
                policy_details = iam_client.get_policy(PolicyArn=policy_arn)
                policy_version = iam_client.get_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=policy_details['Policy']['DefaultVersionId']
                )
                policy_document = policy_version['PolicyVersion']['Document']

                # Check if the policy allows administrative privileges
                if 'Statement' in policy_document:
                    for statement in policy_document['Statement']:
                        # Check for Allow effect and admin privileges
                        if statement.get('Effect') == 'Allow' and (
                            '*:*' in statement.get('Action', []) or 
                            '*' in statement.get('Action', [])
                        ):
                            findings.append(f"User {user_name} has attached policy {policy['PolicyName']} with administrative privileges.")
                            break  # Break if you found an admin policy for this user

        # Determine report status based on findings
        if findings:
            report.passed = False  # Indicate that the check failed
            report.resource_ids_status = {user['UserName']: False for user in users}  # Mark all users as having issues
            report.report_metadata = {"findings": findings}  # Store findings in report metadata
        else:
            report.passed = True  # Indicate that the check passed
            report.resource_ids_status = {user['UserName']: True for user in users}  # Mark all users as having no issues

        return report
    
    
# Green Tick: The check passed because, according to the criteria in the code, it did not find any users whose attached policies explicitly grant administrative privileges based on the specific check logic.
# Red Cross: The check would indicate a failure (red cross) if it finds users whose policies meet the specified condition for administrative access.
