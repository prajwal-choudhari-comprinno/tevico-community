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


class ec2_ebs_snapshot_encrypted(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        ec2_client = connection.client('ec2')
        report = CheckReport(name=__name__)
        report.resource_ids_status = []
        has_unencrypted = False  # Track unencrypted snapshots

        try:
            paginator = ec2_client.get_paginator('describe_snapshots')

            for page in paginator.paginate(OwnerIds=['self']):  # Paginate automatically
                snapshots = page.get('Snapshots', [])

                if not snapshots:  # If empty page and no previous snapshots
                    continue

                for snapshot in snapshots:
                    snapshot_id = snapshot['SnapshotId']
                    encrypted = snapshot.get('Encrypted', False)

                    status = CheckStatus.PASSED if encrypted else CheckStatus.FAILED
                    summary = f"EBS snapshot {snapshot_id} is {'encrypted' if encrypted else 'not encrypted'}."

                    if not encrypted:
                        has_unencrypted = True  # Track unencrypted snapshots

                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=snapshot_id),
                            status=status,
                            summary=summary
                        )
                    )

            if not report.resource_ids_status:  # If no snapshots exist
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No EBS snapshots found."
                    )
                )
            else:
                report.status = CheckStatus.FAILED if has_unencrypted else CheckStatus.PASSED

        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary="Error retrieving EBS snapshot encryption status.",
                    exception=str(e)
                )
            )

        return report
