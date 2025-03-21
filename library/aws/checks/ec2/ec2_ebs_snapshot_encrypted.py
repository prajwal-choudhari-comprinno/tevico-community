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
        has_unencrypted = False  # Track failed status
        next_token = None

        try:
            while True:
                response = ec2_client.describe_snapshots(OwnerIds=['self'], NextToken=next_token) if next_token else ec2_client.describe_snapshots(OwnerIds=['self'])
                snapshots = response.get('Snapshots', [])
                next_token = response.get('NextToken', None)  # Ensure we handle missing NextToken

                if not snapshots:
                    if next_token is None:  # If no snapshots and no pagination, mark as NOT_APPLICABLE
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name="EBS Snapshots"),
                                status=CheckStatus.NOT_APPLICABLE,
                                summary="No EBS snapshots found."
                            )
                        )
                        return report
                    continue  # If NextToken exists, continue pagination

                for snapshot in snapshots:
                    snapshot_id = snapshot['SnapshotId']
                    encrypted = snapshot.get('Encrypted', False)

                    status = CheckStatus.PASSED if encrypted else CheckStatus.FAILED
                    summary = f"EBS snapshot {snapshot_id} is {'encrypted' if encrypted else 'not encrypted'}."

                    if not encrypted:
                        has_unencrypted = True  # Track failed status

                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=snapshot_id),
                            status=status,
                            summary=summary
                        )
                    )

                if not next_token:  # Exit loop if there are no more pages
                    break

            report.status = CheckStatus.FAILED if has_unencrypted else CheckStatus.PASSED

        except (BotoCoreError, ClientError) as e:
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="EBS Snapshots"),
                    status=CheckStatus.UNKNOWN,
                    summary="Error retrieving EBS snapshot encryption status.",
                    exception=str(e)
                )
            )

        return report
