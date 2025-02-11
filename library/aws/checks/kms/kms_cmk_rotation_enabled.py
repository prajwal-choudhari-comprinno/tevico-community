"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-12
"""

import boto3
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, ResourceStatus, GeneralResource
from tevico.engine.entities.check.check import Check

class kms_cmk_rotation_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED  # Default to PASSED unless non-compliant keys are found
        report.resource_ids_status = []

        try:
            client = connection.client('kms')
            paginator = client.get_paginator('list_keys')

            non_compliant_keys_found = False

            for page in paginator.paginate():
                for key in page.get('Keys', []):
                    key_id = key['KeyId']
                    # Get key details to check if it's customer-managed and enabled
                    key_info = client.describe_key(KeyId=key_id)
                    key_metadata = key_info.get('KeyMetadata', {})

                    try:
                        key_manager = key_metadata.get('KeyManager')
                        key_state = key_metadata.get('KeyState')

                        # Skip AWS-managed keys and disabled keys
                        if key_manager != 'CUSTOMER' or key_state != 'Enabled':
                            continue

                    except ClientError as e:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=key_id),
                                status=CheckStatus.FAILED,
                                summary=f"Failed to describe CMK {key_id}: {str(e)}"
                            )
                        )
                        non_compliant_keys_found = True
                        continue

                    # Check rotation status for customer-managed keys
                    try:
                        rotation_status = client.get_key_rotation_status(KeyId=key_id)
                        rotation_enabled = rotation_status.get('KeyRotationEnabled', False)

                        resource_status = ResourceStatus(
                            resource=AwsResource(arn=key_metadata.get('Arn', key_id)),
                            status=CheckStatus.PASSED if rotation_enabled else CheckStatus.FAILED,
                            summary=f"Key rotation {'enabled' if rotation_enabled else 'not enabled'} for CMK {key_id}."
                        )

                        report.resource_ids_status.append(resource_status)

                        if not rotation_enabled:
                            non_compliant_keys_found = True

                    except ClientError as e:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=key_metadata.get('Arn')),
                                status=CheckStatus.FAILED,
                                summary=f"Failed to retrieve rotation status for CMK {key_id}: {str(e)}"
                            )
                        )
                        non_compliant_keys_found = True

            # Set overall check status based on non-compliant keys
            if non_compliant_keys_found:
                report.status = CheckStatus.FAILED

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
