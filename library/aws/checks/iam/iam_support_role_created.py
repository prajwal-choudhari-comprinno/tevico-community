"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-15
"""

import boto3
import logging

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus, AwsResource
from tevico.engine.entities.check.check import Check


class iam_support_role_created(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        # Initialize IAM and STS clients
        iam_client = connection.client('iam')
        sts_client = connection.client('sts')

        # Define constants
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        required_policy_name = "AWSSupportAccess"
        role_arn_template = "arn:aws:iam::{}:role/{}"

        try:
            # Get AWS Account ID
            account_id = sts_client.get_caller_identity()["Account"]

            # Step 1: Check if the AWSSupportAccess policy exists
            policy_arn = None
            policies = iam_client.list_policies(Scope='AWS', OnlyAttached=False)['Policies']
            for policy in policies:
                if policy['PolicyName'] == required_policy_name:
                    policy_arn = policy['Arn']
                    break

            if not policy_arn:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.FAILED,
                        summary=f"{required_policy_name}: IAM Policy does not exist."
                    )
                )
                return report

            # Step 2: Check if the policy is attached to any roles
            paginator = iam_client.get_paginator('list_entities_for_policy')
            attached_roles = []
            for page in paginator.paginate(PolicyArn=policy_arn, EntityFilter='Role'):
                attached_roles.extend(page['PolicyRoles'])
            if attached_roles:
                role_names = [role['RoleName'] for role in attached_roles]

                for role_name in role_names:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=role_arn_template.format(account_id, role_name)),
                            status=CheckStatus.PASSED,
                            summary=f"Support Role created and IAM policy, {required_policy_name} is attached to it."
                        )
                    )

                # Step 3: Ensure a support-specific role exists
                if not attached_roles:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=""),
                            status=CheckStatus.FAILED,
                            summary=f"No support-specific IAM role found with IAM policy attached."
                        )
                    )
            else:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=AwsResource(arn=policy_arn),
                        status=CheckStatus.FAILED,
                        summary=f"{required_policy_name}: Policy is not attached to any IAM roles."
                    )
                )

        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.ERRORED,
                    summary=f"Error occurred while checking access key rotation",
                    exception=str(e)
                )
            )
            

        return report
