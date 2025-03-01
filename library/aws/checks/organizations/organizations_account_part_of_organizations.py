"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-10-17
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check
from datetime import datetime

class organizations_account_part_of_organizations(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize the Organizations client
            org_client = connection.client('organizations')

            # Fetch list of AWS Organizations
            organizations_list = org_client.list_roots().get('Roots', [])

            if not organizations_list:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.FAILED,
                        summary="No AWS Organizations found for this account."
                    )
                )
                return report  # Return early if no organization exists

            for organization in organizations_list:
                org_id = organization['Id']
                org_arn = organization['Arn']

                # Construct AWS resource ARN for the organization
                resource = AwsResource(arn=org_arn)

                # Check if AWS Organizations is enabled
                org_status = organization.get('PolicyTypes', [{}])[0].get('Status', 'DISABLED')  

                if org_status == "ENABLED":
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.PASSED,
                            summary=f"AWS Organization {org_id} contains this AWS account."
                        )
                    )

                    # Fetch accounts in the organization
                    accounts = org_client.list_accounts().get('Accounts', [])

                    for account in accounts:
                        account_id = account['Id']
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=f"arn:aws:organizations::{connection.client('sts').get_caller_identity()['Account']}:account/{account_id}"),
                                status=CheckStatus.PASSED,
                                summary=f"Account {account_id} is part of AWS Organization {org_id}."
                            )
                        )

                else:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=f"AWS Organization {org_id} is not in use for this AWS account."
                        )
                    )

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing AWS Organizations: {str(e)}"
                )
            )

        return report
