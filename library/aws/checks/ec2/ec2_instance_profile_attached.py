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


class ec2_instance_profile_attached(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        ec2_client = connection.client('ec2')
        report = CheckReport(name=__name__)
        report.resource_ids_status = []

        try:
            # Get all running EC2 instances (exclude pending, terminated)
            paginator = ec2_client.get_paginator('describe_instances')
            has_running_instances = False

            for page in paginator.paginate():
                reservations = page.get('Reservations', [])
                if reservations:
                    has_running_instances = True
                
                for reservation in reservations:
                    for instance in reservation.get('Instances', []):
                        state = instance.get('State', {}).get('Name', '').lower()
                        if state in ["pending", "terminated"]:
                            continue  # Skip these states

                        instance_id = instance['InstanceId']
                        iam_instance_profile = instance.get('IamInstanceProfile')

                        if iam_instance_profile:
                            status = CheckStatus.PASSED
                            summary = f"EC2 instance {instance_id} has an instance profile attached."
                        else:
                            status = CheckStatus.FAILED
                            summary = f"EC2 instance {instance_id} does NOT have an instance profile attached."

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name=instance_id),
                                status=status,
                                summary=summary
                            )
                        )

            # If no running EC2 instances were found, return NOT_APPLICABLE
            if not has_running_instances:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No running EC2 instances found."
                    )
                )
                return report

        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary="Error retrieving EC2 instance profile information.",
                    exception=str(e)
                )
            )

        return report
