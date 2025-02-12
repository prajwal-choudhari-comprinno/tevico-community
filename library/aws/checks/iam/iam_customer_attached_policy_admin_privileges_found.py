"""
AUTHOR: RONIT CHAUHAN 
DATE: 2024-10-11
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_customer_attached_policy_admin_privileges_found(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize IAM client
            iam_client = connection.client('iam')

            # Fetch all IAM users
            users = iam_client.list_users().get('Users', [])
            for user in users:
                user_name = user['UserName']
                user_arn = user['Arn']
                
                # Construct AWS resource ARN for the IAM user
                resource = AwsResource(arn=user_arn)

                try:
                    # Fetch attached policies for the user (only custom managed policies)
                    attached_policies = iam_client.list_attached_user_policies(UserName=user_name).get('AttachedPolicies', [])

                    for policy in attached_policies:
                        policy_arn = policy['PolicyArn']

                        # Fetch policy details
                        policy_details = iam_client.get_policy(PolicyArn=policy_arn)
                        if policy_details['Policy']['Arn'].startswith('arn:aws:iam::aws:policy/'):
                            # Skip AWS managed policies
                            continue

                        # Get the policy document
                        policy_version = policy_details['Policy']['DefaultVersionId']
                        policy_document = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version).get('PolicyVersion', {}).get('Document', {})

                        # Check if the policy grants full administrative privileges
                        has_admin_privileges = False
                        if 'Statement' in policy_document:
                            for statement in policy_document['Statement']:
                                if statement.get('Effect') == 'Allow':
                                    actions = statement.get('Action', [])
                                    resources = statement.get('Resource', [])

                                    # Check if actions allow all actions and resources
                                    if actions == "*" and resources == "*":
                                        has_admin_privileges = True
                                        break
                                    elif isinstance(actions, list) and "*" in actions and isinstance(resources, list) and "*" in resources:
                                        has_admin_privileges = True
                                        break

                        # Append the result for this user
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED if has_admin_privileges else CheckStatus.PASSED,
                                summary=f"User {user_name} {'has' if has_admin_privileges else 'does not have'} custom managed policy with full administrative privileges."
                            )
                        )

                        # If any user has admin privileges, mark overall check as failed
                        if has_admin_privileges:
                            report.status = CheckStatus.FAILED

                except Exception as e:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=f"Error checking policies for user {user_name}: {str(e)}"
                        )
                    )

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing IAM: {str(e)}"
                )
            )

        return report
