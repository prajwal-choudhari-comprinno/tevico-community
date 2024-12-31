"""
AUTHOR: RONIT CHAUHAN 
DATE: 2024-10-11

Description: This security check identifies AWS users who have:
1. Full administrative access (*:*) through their inline policies
2. No inline policies at all (which is a security concern)

Note: Service-specific wildcards (like ec2:*) are allowed and won't trigger failures.
"""

import boto3
import logging
import json
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

# Set up logging
logger = logging.getLogger(__name__)

class iam_inline_policy_admin_privileges_found(Check):
    """
    Security check that examines AWS IAM users' permissions.
    - Fails only for full administrative access (*:*)
    - Allows service-specific wildcards (like ec2:*)
    - Ensures users have at least one inline policy
    """

    def normalize_policy_statement(self, statement):
        """
        Converts policy statements into a standard format for checking.
        Handles different input formats (string, dict, list) and normalizes them.

        Args:
            statement: Raw policy statement

        Returns:
            List of normalized policy statements or None if invalid
        """
        try:
            # Handle JSON string input
            if isinstance(statement, str):
                try:
                    statement = json.loads(statement)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON in policy statement: {e}")
                    return None

            # Convert to list format
            if isinstance(statement, dict):
                statement = [statement]
            elif not isinstance(statement, list):
                logger.warning(f"Invalid statement type: {type(statement)}")
                return None

            normalized_statements = []
            for stmt in statement:
                if not isinstance(stmt, dict):
                    logger.warning(f"Statement must be a dictionary: {type(stmt)}")
                    continue

                # Get and validate Effect
                effect = stmt.get('Effect', '')
                if not isinstance(effect, str):
                    logger.warning(f"Effect must be string, got: {type(effect)}")
                    continue

                # Normalize Action field
                actions = stmt.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]
                elif not isinstance(actions, list):
                    logger.warning(f"Invalid Action format: {type(actions)}")
                    continue

                # Normalize Resource field
                resources = stmt.get('Resource', [])
                if isinstance(resources, str):
                    resources = [resources]
                elif not isinstance(resources, list):
                    logger.warning(f"Invalid Resource format: {type(resources)}")
                    continue

                normalized_statements.append({
                    'Effect': effect,
                    'Action': actions,
                    'Resource': resources
                })

            return normalized_statements

        except Exception as e:
            logger.error(f"Error normalizing statement: {str(e)}")
            return None

    def has_admin_privileges(self, statement):
        """
        Checks if a policy statement grants full administrative access (*:*).
        Allows service-specific wildcards like ec2:*.

        Args:
            statement: Policy statement to check

        Returns:
            bool: True if full admin privileges (*:*) found, False otherwise
        """
        try:
            normalized_statements = self.normalize_policy_statement(statement)
            if not normalized_statements:
                return False

            for stmt in normalized_statements:
                effect = stmt.get('Effect', '').lower()
                actions = stmt.get('Action', [])
                resources = stmt.get('Resource', [])

                # Only check "allow" statements
                if effect != 'allow':
                    continue

                # Check for full admin access (*:*)
                has_full_admin = any(
                    action == '*' for action in actions  # Only exact '*' matches
                )
                has_wildcard_resource = any(
                    resource == '*' for resource in resources  # Only exact '*' matches
                )

                # Log service-specific wildcards (but don't fail for them)
                service_wildcards = [
                    action for action in actions
                    if isinstance(action, str) and action.endswith(':*')
                ]
                if service_wildcards:
                    logger.info(f"Found allowed service-specific wildcards: {service_wildcards}")

                # Only fail for full admin access (*:*)
                if has_full_admin and has_wildcard_resource:
                    logger.warning("Found full administrative access (*:*)")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking admin privileges: {str(e)}")
            return False

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main function that runs the security check.
        Examines all users' inline policies for full admin access.

        Args:
            connection: AWS session for accessing IAM

        Returns:
            CheckReport: Results of the security check
        """
        report = CheckReport(name=__name__)
        
        try:
            # Get list of IAM users
            iam_client = connection.client('iam')
            response = iam_client.list_users()
            users = response.get('Users', [])
            logger.info(f"Starting check for {len(users)} IAM users")
        except (BotoCoreError, ClientError) as e:
            error_message = f"Cannot access AWS IAM: {str(e)}"
            logger.error(error_message)
            report.passed = False
            report.report_metadata = {"error": error_message}
            return report

        findings = []
        resource_ids_status = {}

        # Check each user
        for user in users:
            user_name = user.get('UserName')
            if not user_name:
                logger.warning("Found user without name - skipping")
                continue

            try:
                # Get user's inline policies
                policy_response = iam_client.list_user_policies(UserName=user_name)
                inline_policies = policy_response.get('PolicyNames', [])

                # Check for users with no policies
                if not inline_policies:
                    resource_ids_status[f"{user_name}:no_inline_policies"] = False
                    finding = f"Security Warning: User {user_name} has no inline policies"
                    logger.warning(finding)
                    findings.append(finding)
                    continue

                # Check each policy
                for policy_name in inline_policies:
                    try:
                        policy_response = iam_client.get_user_policy(
                            UserName=user_name,
                            PolicyName=policy_name
                        )
                        
                        policy_document = policy_response.get('PolicyDocument')
                        if not policy_document:
                            logger.warning(f"Empty policy found: {policy_name}")
                            resource_ids_status[f"{user_name}:{policy_name}"] = False
                            continue

                        # Parse JSON policy if needed
                        if isinstance(policy_document, str):
                            try:
                                policy_document = json.loads(policy_document)
                            except json.JSONDecodeError as e:
                                logger.error(f"Invalid JSON in policy {policy_name}: {e}")
                                resource_ids_status[f"{user_name}:{policy_name}"] = False
                                continue

                        # Check for admin privileges
                        statements = policy_document.get('Statement', [])
                        if self.has_admin_privileges(statements):
                            finding = (f"SECURITY ALERT: User {user_name} has full admin "
                                     f"access (*:*) through policy {policy_name}")
                            logger.warning(finding)
                            findings.append(finding)
                            resource_ids_status[f"{user_name}:{policy_name}"] = False
                        else:
                            resource_ids_status[f"{user_name}:{policy_name}"] = True

                    except (BotoCoreError, ClientError) as e:
                        error_message = (f"Error reading policy {policy_name} for "
                                       f"user {user_name}: {str(e)}")
                        logger.error(error_message)
                        findings.append(error_message)
                        resource_ids_status[f"{user_name}:{policy_name}"] = False

            except (BotoCoreError, ClientError) as e:
                error_message = f"Error checking user {user_name}: {str(e)}"
                logger.error(error_message)
                findings.append(error_message)
                resource_ids_status[f"{user_name}:error"] = False

        # Prepare final report
        report.passed = all(resource_ids_status.values())
        report.resource_ids_status = resource_ids_status
        report.report_metadata = {
            "findings": findings,
            "details": {
                resource_id: {
                    "status": "passed" if status else "failed",
                    "user": resource_id.split(":")[0] if ":" in resource_id else "unknown",
                    "policy": resource_id.split(":")[1] if ":" in resource_id else "unknown"
                }
                for resource_id, status in resource_ids_status.items()
            }
        }
        
        logger.info(f"Security check completed - Found {len(findings)} issues")
        return report


# What this security check does:
# 1. Fails (returns False) if:
#    - A user has full admin access (*:*)
#    - A user has no inline policies defined
#    - We can't verify a user's policies
#
# 2. Passes (returns True) if:
#    - Users have appropriate access (including service-specific wildcards like ec2:*)
#    - No users have full administrative privileges
#
# 3. Allows service-specific wildcards:
#    - ec2:* (all EC2 permissions)
#    - s3:* (all S3 permissions)
#    - etc.
