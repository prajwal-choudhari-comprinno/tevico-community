"""
AUTHOR: Sheikh Aafaq Rashid
DATE: 10-10-2024
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, AwsResource, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class ec2_ebs_default_encryption(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
         # Initialize EC2 client
        client = connection.client('ec2')

        report = CheckReport(name=__name__)

        # Initialize report status
        report.status = CheckStatus.PASSED  # Assume passed unless default encryption is not enabled
        report.resource_ids_status = []

        try:
            # Fetch EBS default encryption status
            
            res = client.get_ebs_encryption_by_default()
      
            default_encryption_enabled = res.get('EbsEncryptionByDefault', False)

            if not default_encryption_enabled:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(resource=""),
                        status=CheckStatus.FAILED,
                        summary=f"Default EBS Encryption Disabled"
                    )
                )

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error while checking EBS default encryption",
                    exception=e
                )
            )

        return report