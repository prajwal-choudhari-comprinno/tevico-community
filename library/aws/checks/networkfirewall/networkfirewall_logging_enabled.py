"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-13
"""

import boto3
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class networkfirewall_logging_enabled(Check):
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

            for firewall in firewalls:
                firewall_name = firewall['FirewallName']
                firewall_arn = firewall['FirewallArn']

                try:
                    logging_config = client.describe_logging_configuration(FirewallArn=firewall_arn)
                    log_destinations = logging_config.get('LoggingConfiguration', {}).get('LogDestinationConfigs', [])

                    is_logging_enabled = bool(log_destinations)

                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=firewall_arn),
                            status=CheckStatus.PASSED if is_logging_enabled else CheckStatus.FAILED,
                            summary=f"Logging {'enabled' if is_logging_enabled else 'disabled'} for {firewall_name}."
                        )
                    )

                    if not is_logging_enabled:
                        report.status = CheckStatus.FAILED  # At least one firewall is non-compliant

                except client.exceptions.ResourceNotFoundException:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=firewall_arn),
                            status=CheckStatus.FAILED,
                            summary=f"Firewall {firewall_name} not found.",
                            exception=client.exceptions.ResourceNotFoundException
                        )
                    )
                    report.status = CheckStatus.FAILED

                except Exception as e:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=firewall_arn),
                            status=CheckStatus.FAILED,
                            summary=f"Error retrieving logging config for {firewall_name}: {str(e)}",
                            exception=e
                        )
                    )
                    report.status = CheckStatus.FAILED

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error retrieving firewall list: {str(e)}",
                    exception=e
                )
            )

        return report
