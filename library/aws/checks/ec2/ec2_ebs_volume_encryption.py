"""
AUTHOR: Sheikh Aafaq Rashid
DATE: 10-10-2024
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import (
    CheckReport, CheckStatus, GeneralResource, ResourceStatus
)
from tevico.engine.entities.check.check import Check


class ec2_ebs_volume_encryption(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        ec2_client = connection.client('ec2')
        report = CheckReport(name=__name__)
        report.resource_ids_status = []
        has_unencrypted = False  # Track unencrypted volumes

        try:
            paginator = ec2_client.get_paginator('describe_volumes')
            for page in paginator.paginate():  # Paginate automatically
                volumes = page.get('Volumes', [])

                if not volumes:  # If empty page and no previous volumes
                    continue

                for volume in volumes:
                    volume_id = volume['VolumeId']
                    encrypted = volume.get('Encrypted', False)

                    status = CheckStatus.PASSED if encrypted else CheckStatus.FAILED
                    summary = f"EBS volume {volume_id} is {'encrypted' if encrypted else 'not encrypted'}."

                    if not encrypted:
                        has_unencrypted = True  # Track unencrypted volumes

                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=volume_id),
                            status=status,
                            summary=summary
                        )
                    )

            if not report.resource_ids_status:  # If no volumes at all
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name="EBS Volumes"),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No EBS volumes found."
                    )
                )
            else:
                report.status = CheckStatus.FAILED if has_unencrypted else CheckStatus.PASSED

        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="EBS Volumes"),
                    status=CheckStatus.UNKNOWN,
                    summary="Error retrieving EBS volume encryption status.",
                    exception=str(e)
                )
            )

        return report
