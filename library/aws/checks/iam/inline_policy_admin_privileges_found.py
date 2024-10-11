"""
AUTHOR: RONIT CHAUHAN
DATE: 11-10-24
"""

import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class inline_policy_admin_privileges_found(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        # Create a report object to hold the result of the check
        report = CheckReport(name=__name__)
        
        # Initialize the IAM client using the provided connection session
        iam_client = connection.client('iam')

        # Initialize an empty list to store any findings
        findings = []

        # Fetch all users and check their inline policies
        paginator = iam_client.get_paginator('list_users')
        for page in paginator.paginate():
            for user in page['Users']:
                user_name = user['UserName']

                # Fetch inline policies attached to the user
                inline_policies = iam_client.list_user_policies(UserName=user_name)
                for policy_name in inline_policies['PolicyNames']:
                    policy_document = iam_client.get_user_policy(
                        UserName=user_name,
                        PolicyName=policy_name
                    )['PolicyDocument']

                    # Check if the inline policy contains administrative privileges
                    if self._has_admin_privileges(policy_document):
                        findings.append(f"User {user_name} has an inline policy {policy_name} with administrative privileges.")
                        report.resource_ids_status[user_name] = False  # Mark the user as having an issue
                        report.passed = False  # The check failed since admin privileges were found
                    else:
                        report.resource_ids_status[user_name] = True  # No issues found for this user

        # Attach any findings to the report metadata
        report.report_metadata = {"findings": findings}
        return report

    def _has_admin_privileges(self, policy_document: Dict[str, Any]) -> bool:
        """Check if the policy document contains administrative privileges ('*:*')."""
        for statement in policy_document.get("Statement", []):
            # Check if the statement allows all actions ('*') on all resources ('*')
            if (statement.get("Effect") == "Allow" and
                    ('*' in statement.get("Action", []) or '*:*' in statement.get("Action", [])) and
                    '*' in statement.get("Resource", [])):
                return True
        return False

