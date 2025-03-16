"""
AUTHOR: RONIT CHAUHAN 
DATE: 2024-10-11
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_customer_unattached_policy_admin_privileges_found(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize IAM client
            iam_client = connection.client('iam')

            # Fetch all custom managed policies
            policies = iam_client.list_policies(Scope='Local').get('Policies', [])

            for policy in policies:
                policy_arn = policy['Arn']
                policy_name = policy['PolicyName']

                # Construct AWS resource ARN for the IAM policy
                resource = AwsResource(arn=policy_arn)

                # Check if the policy is unattached
                if policy['AttachmentCount'] == 0:
                    try:
                        # Fetch policy details
                        policy_details = iam_client.get_policy(PolicyArn=policy_arn)

                        # Get the policy document
                        policy_version = policy_details['Policy']['DefaultVersionId']
                        policy_document = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version).get('PolicyVersion', {}).get('Document', {})

                        has_admin_privileges = False

                        # Check if the policy grants full administrative privileges
                        if 'Statement' in policy_document:
                            if isinstance(policy_document['Statement'], dict):
                                policy_document['Statement'] = [policy_document['Statement']]

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

                        # Append the result for this policy
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED if has_admin_privileges else CheckStatus.PASSED,
                                summary=f"Policy {policy_name} {'grants' if has_admin_privileges else 'does not grant'} full administrative privileges while being unattached."
                            )
                        )

                        # If any unattached policy has admin privileges, mark overall check as failed
                        if has_admin_privileges:
                            report.status = CheckStatus.FAILED

                    except Exception as e:
                        report.status = CheckStatus.FAILED
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Error checking policy {policy_name}: {str(e)}"
                            )
                        )

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing IAM: {str(e)}"
                )
            )

        return report
