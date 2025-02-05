"""
AUTHOR: Sheikh Aafaq Rashid
DATE: 10-10-2024
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, AwsResource, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class ec2_ebs_snapshot_encrypted(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:

        # Initialize EC2 client
        client = connection.client('ec2')

        report = CheckReport(name=__name__)

        # Initialize report status
        report.status = CheckStatus.PASSED  # Assume passed unless we find an unencrypted snapshot
        report.resource_ids_status = []

        try:
            # Fetch all snapshots
            res = client.describe_snapshots(OwnerIds=['self'])
            snapshots = res['Snapshots']

            if not snapshots:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(resource=""),
                        status=CheckStatus.SKIPPED,
                        summary=f"No Snapshots found"
                    )
                )

            for snapshot in snapshots:
                snapshot_id = snapshot['SnapshotId']
                encrypted = snapshot.get('Encrypted', False)

                # Log the encryption status of each snapshot
                # Snapshot only has Snapshot Id and no arn
                if not encrypted:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(resource=snapshot_id),
                            status=CheckStatus.FAILED,
                            summary=f"Snapshot {snapshot_id} is not Encrypted."
                        )
                    )


        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error in reading snapshots",
                    exception=e
                )
            )

        return report
