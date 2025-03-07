"""
AUTHOR: Deepak Puri
EMAIL: deepak.puri@comprinno.net
DATE: 2024-10-10
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class ec2_managed_instance_patch_compliance_status(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)

        client = connection.client('ssm')
        
        managed_instances = client.describe_instance_information()['InstanceInformationList']
        report.status = CheckStatus.PASSED  
        
        for instance in managed_instances:
            instance_id = instance['InstanceId']
            
            try:
                patch_states = client.describe_instance_patch_states(InstanceIds=[instance_id])['InstancePatchStates']
                for patch_state in patch_states:
                    if patch_state['ComplianceStatus'] != 'COMPLIANT':
                        report.status = CheckStatus.FAILED
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name=instance_id), # This should be AwsResource
                                status=CheckStatus.FAILED,
                                summary=f"Instance {instance_id} is not compliant"
                            )
                        )
                    else:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name=instance_id), # This should be AwsResource
                                status=CheckStatus.PASSED,
                                summary=f"Instance {instance_id} is compliant"
                            )
                        )
            except Exception as e:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=instance_id), # This should be AwsResource
                        status=CheckStatus.FAILED,
                        summary=f"Failed to get patch compliance status for instance {instance_id}",
                        exception=str(e)
                    )
                )

        return report
        
