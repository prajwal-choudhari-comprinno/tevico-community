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
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        ADMIN_POLICIES = {"AdministratorAccess"}  # List of known admin policies

        def check_policies(entity_name, entity_type, list_policies_func):
            """Helper function to check attached policies for a user, group, or role"""
            resource = AwsResource(arn=f"arn:aws:iam::account-id:{entity_type}/{entity_name}")
            response = list_policies_func(entity_name)
            attached_policies = response.get('AttachedPolicies', [])

            for policy in attached_policies:
                if policy['PolicyName'] in ADMIN_POLICIES:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=f"{entity_type.capitalize()} '{entity_name}' has attached admin policy '{policy['PolicyName']}'."
                        )
                    )
                    report.status = CheckStatus.FAILED
                    return

            report.resource_ids_status.append(
                ResourceStatus(
                    resource=resource,
                    status=CheckStatus.PASSED,
                    summary=f"{entity_type.capitalize()} '{entity_name}' does not have admin privileges."
                )
            )

        try:
            # Check IAM Users
            for user in client.list_users().get('Users', []):
                check_policies(user['UserName'], 'user', lambda name: client.list_attached_user_policies(UserName=name))


            # Check IAM Roles
            for role in client.list_roles().get('Roles', []):
                check_policies(role['RoleName'], 'role', lambda name: client.list_attached_role_policies(RoleName=name))
                
            # Check IAM Groups
            for group in client.list_groups().get('Groups', []):
                check_policies(group['GroupName'], 'group', lambda name: client.list_attached_group_policies(GroupName=name))

        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.ERRORED,
                    summary="Error occurred while checking attached admin policies.",
                    exception=str(e)
                )
            )

        return report