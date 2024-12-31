"""
AUTHOR: RONIT CHAUHAN 
DATE: 2024-10-11

Description: This code checks for AWS users who have too much power (administrative privileges) 
through their inline policies.
"""

import boto3
import logging
import json
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

logger = logging.getLogger(__name__)

class iam_inline_policy_admin_privileges_found(Check):
    """
    This check looks for AWS users who might have too much power through their inline policies.
    """

    def normalize_policy_statement(self, statement):
        """
        Normalize policy statement to ensure consistent dictionary format
        """
        try:
            if isinstance(statement, str):
                try:
                    statement = json.loads(statement)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in policy statement: {statement}")
                    return None

            if not isinstance(statement, dict):
                logger.warning(f"Statement is not a dictionary: {statement}")
                return None

            effect = statement.get('Effect', '')
            if not isinstance(effect, str):
                return None

            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            elif not isinstance(actions, list):
                actions = []

            resources = statement.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]
            elif not isinstance(resources, list):
                resources = []

            return {
                'Effect': effect,
                'Action': actions,
                'Resource': resources
            }

        except Exception as e:
            logger.error(f"Error normalizing statement: {e}")
            return None

    def has_admin_privileges(self, statement):
        """
        Check if normalized statement grants admin privileges
        """
        normalized = self.normalize_policy_statement(statement)
        if not normalized:
            return False

        effect = normalized['Effect'].lower()
        actions = normalized['Action']
        resources = normalized['Resource']

        if effect != 'allow':
            return False

        has_wildcard_action = '*' in actions or any('*' in action for action in actions)
        has_wildcard_resource = '*' in resources or any('*' in resource for resource in resources)

        return has_wildcard_action and has_wildcard_resource

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main function that checks for users with administrative privileges.
        """
        report = CheckReport(name=__name__)
        
        try:
            iam_client = connection.client('iam')
            users = iam_client.list_users()['Users']
            logger.info(f"Found {len(users)} IAM users to check")
        except (BotoCoreError, ClientError) as e:
            error_message = f"AWS IAM service error: {str(e)}"
            logger.error(error_message)
            report.passed = False
            report.report_metadata = {"error": error_message}
            return report

        findings = []
        resource_ids_status = {}

        for user in users:
            user_name = user['UserName']
            logger.info(f"Checking policies for user: {user_name}")

            try:
                inline_policies = iam_client.list_user_policies(UserName=user_name)['PolicyNames']
            except (BotoCoreError, ClientError) as e:
                error_message = f"Cannot check policies for user {user_name}: {str(e)}"
                logger.error(error_message)
                resource_ids_status[f"{user_name}:no_policies_found"] = False
                findings.append(error_message)
                continue

            if not inline_policies:
                # Mark users with no inline policies as failed
                resource_ids_status[f"{user_name}:no_inline_policies"] = False
                finding = f"User {user_name} has no inline policies"
                logger.info(finding)
                findings.append(finding)
                continue

            for policy_name in inline_policies:
                try:
                    policy_response = iam_client.get_user_policy(
                        UserName=user_name, 
                        PolicyName=policy_name
                    )
                    
                    policy_document = policy_response['PolicyDocument']

                    if isinstance(policy_document, str):
                        try:
                            policy_document = json.loads(policy_document)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON in policy document for {policy_name}")
                            resource_ids_status[f"{user_name}:{policy_name}"] = False
                            continue

                    statements = policy_document.get('Statement', [])
                    if not isinstance(statements, list):
                        statements = [statements]

                    has_admin_privileges = False
                    for statement in statements:
                        if self.has_admin_privileges(statement):
                            has_admin_privileges = True
                            finding = f"SECURITY ALERT: User {user_name} has full admin access through policy {policy_name}"
                            logger.warning(finding)
                            findings.append(finding)
                            break

                    # Create resource ID with both user name and policy name
                    resource_id = f"{user_name}:{policy_name}"
                    resource_ids_status[resource_id] = not has_admin_privileges

                except (BotoCoreError, ClientError) as e:
                    error_message = f"Error reading policy {policy_name} for user {user_name}: {str(e)}"
                    logger.error(error_message)
                    findings.append(error_message)
                    resource_ids_status[f"{user_name}:{policy_name}"] = False

        # Prepare final report
        report.passed = all(status for status in resource_ids_status.values())
        report.resource_ids_status = resource_ids_status
        
        report.report_metadata = {
            "findings": findings,
            "details": {
                resource_id: {
                    "status": "passed" if status else "failed",
                    "user": resource_id.split(":")[0],
                    "policy": resource_id.split(":")[1]
                }
                for resource_id, status in resource_ids_status.items()
            }
        }
        
        logger.info(f"Check completed with {len(findings)} findings")
        return report


# What this check does:
# 1. Passes (returns True) if:
#    - No users have full administrative access through inline policies
#    - All users have appropriate limited access
#
# 2. Fails (returns False) if:
#    - Any user has a policy giving them full access (using "*")
#    - We can't verify a user's policies (treating it as a security risk)
#
# Think of it like a security audit:
# - Looking for employees who might have "master keys" when they should only have specific access
# - Making sure everyone follows the "least privilege" principle (only having access to what they need)
