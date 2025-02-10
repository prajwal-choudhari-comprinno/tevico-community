"""
AUTHOR: Sheikh Aafaq Rashid
DATE: 10-10-2024
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, AwsResource, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class ec2_ebs_volume_encryption(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        # Initialize EC2 client
        client = connection.client('ec2')

        # Fetch all volumes
        res = client.describe_volumes()
        volumes = res['Volumes']
        
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED  # Assume passed unless we find an unencrypted volume
        report.resource_ids_status = []

        if not volumes:
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.SKIPPED,
                    summary=f"No Volumes found"
                )
            )

        for volume in volumes:
            volume_id = volume['VolumeId']
            encrypted = volume.get('Encrypted', False)

            # Log the encryption status of each volume
            if not encrypted:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(resource=volume_id),
                        status=CheckStatus.FAILED,
                        summary=f"Volume {volume_id} is not Encrypted."
                    )
                )

        return report                                       