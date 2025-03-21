"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-15
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import (
    CheckReport, CheckStatus, GeneralResource, ResourceStatus
)
from tevico.engine.entities.check.check import Check


class ec2_imdsv2_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        ec2_client = connection.client('ec2')
        report = CheckReport(name=__name__)
        report.resource_ids_status = []
        has_non_compliant = False  # Track instances that fail the check

        try:
            paginator = ec2_client.get_paginator('describe_instances')

            for page in paginator.paginate():
                reservations = page.get('Reservations', [])

                if not reservations:
                    continue

                for reservation in reservations:
                    for instance in reservation.get('Instances', []):
                        instance_id = instance['InstanceId']

                        # Fetch Metadata Options
                        metadata_options = instance.get('MetadataOptions', {})
                        http_tokens = metadata_options.get('HttpTokens', 'optional')  # Default is 'optional'
                        http_endpoint = metadata_options.get('HttpEndpoint', 'disabled')  # Default is 'disabled'

                        # Determine compliance level
                        if http_endpoint.lower() == 'disabled' or http_tokens.lower() == 'optional':
                            status = CheckStatus.FAILED
                            summary = f"EC2 instance {instance_id} does not enforce IMDSv2."
                            has_non_compliant = True
                        elif http_tokens == 'required':
                            status = CheckStatus.PASSED
                            summary = f"EC2 instance {instance_id} enforces IMDSv2."

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name=instance_id),
                                status=status,
                                summary=summary
                            )
                        )

            if not report.resource_ids_status:  # If no instances exist
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No EC2 instances found."
                    )
                )
            else:
                report.status = CheckStatus.FAILED if has_non_compliant else CheckStatus.PASSED

        except (BotoCoreError, ClientError) as e:
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary="Error retrieving EC2 instance metadata options.",
                    exception=str(e)
                )
            )

        return report
