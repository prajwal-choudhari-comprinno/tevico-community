"""
AUTHOR: RONIT CHAUHAN
DATE: 11-10-24
"""

import boto3
from typing import Dict, Any, List
from datetime import datetime
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class customer_unattached_policy_admin_privileges_found(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        # Create a report object to hold the result of the check
        report = CheckReport(name=__name__)
        report.created_on = datetime.now()  # Track when the check was created
        
        # Initialize the IAM client using the provided connection session
        iam_client = connection.client('iam')

        # Initialize an empty list to store any findings
        findings = []
        report.passed = True  # Assume the check passes unless an issue is found

        # Fetch all customer-managed policies
        paginator = iam_client.get_paginator('list_policies')
        for page in paginator.paginate(Scope='Local'):
            for policy in page['Policies']:
                policy_arn = policy['Arn']
                policy_name = policy['PolicyName']
                attachment_count = policy['AttachmentCount']
                
                # Check only for unattached policies
                if attachment_count == 0:
                    print(f"Checking unattached policy {policy_name}")

                    # Get the policy document
                    policy_document = iam_client.get_policy_version(
                        PolicyArn=policy_arn,
                        VersionId=iam_client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
                    )['PolicyVersion']['Document']

                    # Check if the unattached policy contains administrative privileges
                    if self._has_admin_privileges(policy_document):
                        findings.append(f"Unattached policy {policy_name} has administrative privileges.")
                        report.passed = False  # The check failed since admin privileges were found
                    else:
                        print(f"Unattached policy {policy_name} does not have administrative privileges.")

        # Attach any findings to the report metadata
        report.report_metadata = {"findings": findings}
        return report

    def _has_admin_privileges(self, policy_document: Dict[str, Any]) -> bool:
        """Check if the policy document contains administrative privileges ('*:*', 'service_name:*', '*:service_name')."""
        for statement in policy_document.get("Statement", []):
            if statement.get("Effect") == "Allow":
                actions = statement.get("Action", [])
                resources = statement.get("Resource", [])
                
                # Check for various patterns indicating admin privileges
                if (
                    ('*' in actions or '*:*' in actions) and
                    ('*' in resources or '*' in resources)
                ):
                    return True
                # Check for specific service-based permissions
                for action in actions:
                    if ':' in action:
                        service_name = action.split(':')[0]
                        if f"{service_name}:*" in actions or f"*:{service_name}" in actions:
                            return True
        return False
