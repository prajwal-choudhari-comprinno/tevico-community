"""
AUTHOR: SUPRIYO BHAKAT
EMAIL: supriyo.bhakat@comprinno.net
DATE: 2024-11-12
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, AwsResource, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class ssm_patch_manager_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        ssm_client = connection.client('ssm')
        ec2_client = connection.client('ec2')

        instances = ec2_client.describe_instances()['Reservations']

        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                
                try:
                    compliance_info = ssm_client.describe_instance_patch_states(InstanceIds=[instance_id])

                    if compliance_info['InstancePatchStates']:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name=instance_id),
                                status=CheckStatus.PASSED,
                                summary=''
                            )
                        )
                    else:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name=instance_id),
                                status=CheckStatus.FAILED,
                                summary=''
                            )
                        )
                        report.status = CheckStatus.FAILED

                except ssm_client.exceptions.InvalidInstanceId:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=instance_id),
                            status=CheckStatus.FAILED,
                            summary=''
                        )
                    )
                    report.status = CheckStatus.FAILED


        return report
