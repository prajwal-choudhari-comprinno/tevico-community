"""
AUTHOR: SUPRIYO BHAKAT
EMAIL: supriyo.bhakat@comprinno.net
DATE: 2024-11-08
"""

import boto3
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class networkfirewall_multi_az_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('network-firewall')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            firewalls = client.list_firewalls().get('Firewalls', [])

            if not firewalls:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(resource=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No Network Firewall resources found."
                    )
                )
                return report

            for firewall_info in firewalls:
                firewall_name = firewall_info['FirewallName']
                firewall_details = client.describe_firewall(FirewallName=firewall_name)
                firewall_arn = firewall_details['Firewall']['FirewallArn']

                try:
                    
                    subnet_mappings = firewall_details['Firewall'].get('SubnetMappings', [])

                    is_multi_az = len(subnet_mappings) > 1

                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=firewall_arn),
                            status=CheckStatus.PASSED if is_multi_az else CheckStatus.FAILED,
                            summary=f"Multi-AZ {'enabled' if is_multi_az else 'not enabled'} for {firewall_name}."
                        )
                    )

                    if not is_multi_az:
                        report.status = CheckStatus.FAILED  # At least one firewall is non-compliant

                except client.exceptions.ResourceNotFoundException:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=firewall_arn),
                            status=CheckStatus.FAILED,
                            summary=f"Firewall {firewall_name} not found."
                        )
                    )
                    report.status = CheckStatus.FAILED

                except ClientError as e:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=firewall_arn),
                            status=CheckStatus.FAILED,
                            summary=f"Error retrieving firewall details for {firewall_name}: {str(e)}"
                        )
                    )
                    report.status = CheckStatus.FAILED

        except ClientError as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error retrieving firewall list: {str(e)}"
                )
            )

        return report
