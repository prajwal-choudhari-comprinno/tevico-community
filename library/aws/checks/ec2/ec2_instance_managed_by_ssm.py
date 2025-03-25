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


class ec2_instance_managed_by_ssm(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        ec2_client = connection.client('ec2')
        ssm_client = connection.client('ssm')
        report = CheckReport(name=__name__)
        report.resource_ids_status = []

        try:
            # Get all running EC2 instances (exclude pending, terminated, stopped)
            paginator = ec2_client.get_paginator('describe_instances')
            instance_ids = []
            has_running_instances = False

            for page in paginator.paginate():
                reservations = page.get('Reservations', [])
                # If there are any reservations, mark that we found running instances
                if reservations:
                    has_running_instances = True
                
                for reservation in reservations:
                    for instance in reservation.get('Instances', []):
                        state = instance.get('State', {}).get('Name', '').lower()
                        if state in ["pending", "terminated", "stopped"]:
                            continue  # Skip these states

                        instance_id = instance['InstanceId']
                        instance_ids.append(instance_id)

            # If no EC2 instances were found, return NOT_APPLICABLE
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

            # Get list of SSM-managed instances
            managed_instances = set()
            ssm_paginator = ssm_client.get_paginator('describe_instance_information')

            for page in ssm_paginator.paginate():
                for instance in page.get('InstanceInformationList', []):
                    managed_instances.add(instance['InstanceId'])

            # Compare and classify instances
            for instance_id in instance_ids:
                if instance_id in managed_instances:
                    status = CheckStatus.PASSED
                    summary = f"EC2 instance {instance_id} is managed by SSM."
                else:
                    status = CheckStatus.FAILED
                    summary = f"EC2 instance {instance_id} is NOT managed by SSM."
                   

                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=instance_id),
                        status=status,
                        summary=summary
                    )
                )


        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary="Error retrieving EC2 SSM management status.",
                    exception=str(e)
                )
            )

        return report
