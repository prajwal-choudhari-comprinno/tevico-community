"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-14
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class iam_attached_policy_admin_privileges_found(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('iam')
        sts_client = connection.client('sts')
        
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        # Include both AdministratorAccess and PowerUserAccess policies
        ADMIN_POLICIES = {"AdministratorAccess", "PowerUserAccess"}

        try:
            account_id = sts_client.get_caller_identity()["Account"]  # Get AWS Account ID
        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": "Failed to retrieve AWS account ID."}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="AWS Account"),
                    status=CheckStatus.ERRORED,
                    summary="Failed to retrieve AWS account ID.",
                    exception=str(e)
                )
            )
            return report  # Exit early since we cannot construct ARNs

        def check_policies(entity_name, entity_type, list_policies_func):
            """Helper function to check attached policies for a user, group, or role"""
            resource = AwsResource(arn=f"arn:aws:iam::{account_id}:{entity_type}/{entity_name}")
            paginator = list_policies_func()

            attached_policies = []
            for page in paginator:
                attached_policies.extend(page.get('AttachedPolicies', []))

            for policy in attached_policies:
                if policy['PolicyName'] in ADMIN_POLICIES:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=f"{entity_type.capitalize()} '{entity_name}' has attached high-privilege policy '{policy['PolicyName']}'."
                        )
                    )
                    report.status = CheckStatus.FAILED
                    return

            report.resource_ids_status.append(
                ResourceStatus(
                    resource=resource,
                    status=CheckStatus.PASSED,
                    summary=f"{entity_type.capitalize()} '{entity_name}' does not have admin or power user privileges."
                )
            )

        try:
            # Check IAM Users
            paginator = client.get_paginator('list_users')
            for page in paginator.paginate():
                for user in page.get('Users', []):
                    check_policies(user['UserName'], 'user', lambda: client.get_paginator('list_attached_user_policies').paginate(UserName=user['UserName']))

            # Check IAM Roles
            paginator = client.get_paginator('list_roles')
            for page in paginator.paginate():
                for role in page.get('Roles', []):
                    check_policies(role['RoleName'], 'role', lambda: client.get_paginator('list_attached_role_policies').paginate(RoleName=role['RoleName']))
                
            # Check IAM Groups
            paginator = client.get_paginator('list_groups')
            for page in paginator.paginate():
                for group in page.get('Groups', []):
                    check_policies(group['GroupName'], 'group', lambda: client.get_paginator('list_attached_group_policies').paginate(GroupName=group['GroupName']))

        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="AWS IAM"),
                    status=CheckStatus.ERRORED,
                    summary="Error occurred while checking attached admin policies.",
                    exception=str(e)
                )
            )

        return report
