"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-12
"""

import boto3
from botocore.exceptions import EndpointConnectionError, ClientError
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, ResourceStatus, GeneralResource
from tevico.engine.entities.check.check import Check

class inspector_ec2_scan_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize Inspector2 client
            client = connection.client('inspector2')

            # Get EC2 scanning status using list_coverage
            response = client.list_coverage(
                filterCriteria={
                    'resourceType': [{
                        'comparison': 'EQUALS',
                        'value': 'EC2_INSTANCE'
                    }]
                }
            )

            # If no resources found, mark check as failed
            covered_resources = response.get('coveredResources', [])
            if not covered_resources:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=AwsResource(arn=""),
                        status=CheckStatus.FAILED,
                        summary="No EC2 instances found under AWS Inspector2 coverage."
                    )
                )
                return report  # Early exit

            # Check each EC2 instance's scanning status
            for resource in covered_resources:
                instance_id = resource.get('resourceId')
                scan_status = resource.get('scanStatus', {}).get('statusCode', 'INACTIVE')
                scan_enabled = scan_status == 'ACTIVE'

                resource_status = ResourceStatus(
                    resource=AwsResource(arn=f"arn:aws:ec2:{connection.region_name}::{instance_id}"),
                    status=CheckStatus.PASSED if scan_enabled else CheckStatus.FAILED,
                    summary=f"Inspector2 scanning {'enabled' if scan_enabled else 'disabled'} for EC2 instance {instance_id}."
                )

                report.resource_ids_status.append(resource_status)

                if not scan_enabled:
                    report.status = CheckStatus.FAILED  # Mark overall check as failed if any instance is not scanned

        except (EndpointConnectionError, ClientError) as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=AwsResource(arn=""),
                    status=CheckStatus.FAILED,
                    summary=f"Failed to connect to AWS Inspector2 API: {str(e)}"
                )
            )

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Unexpected error: {str(e)}"
                )
            )

        return report
