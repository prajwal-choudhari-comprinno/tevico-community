"""
AUTHOR: SUPRIYO BHAKAT
EMAIL: supriyo.bhakat@comprinno.net
DATE: 2024-11-12
"""

import boto3
from botocore.exceptions import ClientError

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class ssm_ec2instance_remove_interactive_access_check(Check):
    """
    Check to ensure EC2 instances managed by SSM have interactive access (SSH or SSM Session Manager) removed
    to prevent unauthorized access.
    
    This check verifies:
    1. If running instances are managed by SSM
    2. If instances have SSM document associations that enable interactive shell access
    3. If instances have security groups allowing SSH access (port 22)
    """

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Execute the check to verify if EC2 instances have interactive access removed.
        
        Args:
            connection (boto3.Session): A valid AWS session object.
            
        Returns:
            CheckReport: Report detailing EC2 instances with interactive access status.
        """
        # Initialize report with default PASSED status
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []
        
        try:
            ec2_client = connection.client('ec2')
            ssm_client = connection.client('ssm')
            
            # Get all running EC2 instances
            response = ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            reservations = response.get('Reservations', [])
            
            # If no running instances found, mark as NOT_APPLICABLE
            if not reservations:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name="EC2"),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No running EC2 instances found"
                    )
                )
                return report
                
            # Process each running instance
            for reservation in reservations:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    
                    # Check if instance has SSH access via security groups
                    has_ssh_access = False
                    for sg in instance.get('SecurityGroups', []):
                        sg_id = sg['GroupId']
                        sg_details = ec2_client.describe_security_groups(GroupIds=[sg_id])
                        
                        for sg_detail in sg_details.get('SecurityGroups', []):
                            for rule in sg_detail.get('IpPermissions', []):
                                # Check for port 22 (SSH) access
                                from_port = rule.get('FromPort', 0)
                                to_port = rule.get('ToPort', 0)
                                if (from_port <= 22 <= to_port) and rule.get('IpRanges'):
                                    has_ssh_access = True
                                    break
                    
                    try:
                        # Check if instance is managed by SSM
                        ssm_instance_info = ssm_client.describe_instance_information(
                            Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}]
                        )
                        
                        is_ssm_managed = len(ssm_instance_info.get('InstanceInformationList', [])) > 0
                        
                        if is_ssm_managed:
                            # Check for interactive shell access via SSM document associations
                            session_access_info = ssm_client.list_associations(
                                AssociationFilterList=[{'key': 'InstanceId', 'value': instance_id}]
                            )
                            
                            has_interactive_ssm_access = False
                            for association in session_access_info.get('Associations', []):
                                document_name = association.get('Name', '')
                                if 'AWS-RunShellScript' in document_name or 'AWS-RunPowerShellScript' in document_name:
                                    has_interactive_ssm_access = True
                                    break
                            
                            # Determine overall interactive access status
                            has_interactive_access = has_ssh_access or has_interactive_ssm_access
                            
                            if has_interactive_access:
                                access_methods = []
                                if has_ssh_access:
                                    access_methods.append("SSH (port 22)")
                                if has_interactive_ssm_access:
                                    access_methods.append("SSM shell scripts")
                                    
                                report.resource_ids_status.append(
                                    ResourceStatus(
                                        resource=GeneralResource(name=instance_id),
                                        status=CheckStatus.FAILED,
                                        summary=f"EC2 instance {instance_id} has interactive access enabled via: {', '.join(access_methods)}."
                                    )
                                )
                                report.status = CheckStatus.FAILED
                            else:
                                report.resource_ids_status.append(
                                    ResourceStatus(
                                        resource=GeneralResource(name=instance_id),
                                        status=CheckStatus.PASSED,
                                        summary=f"EC2 instance {instance_id} does not have interactive access enabled."
                                    )
                                )
                        else:
                            # Instance not managed by SSM
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=GeneralResource(name=instance_id),
                                    status=CheckStatus.NOT_APPLICABLE,
                                    summary=f"EC2 instance {instance_id} is not managed by SSM."
                                )
                            )
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', '')
                        if error_code == 'InvalidInstanceId':
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=GeneralResource(name=instance_id),
                                    status=CheckStatus.UNKNOWN,
                                    summary=f"EC2 instance {instance_id} is not valid or not accessible via SSM."
                                )
                            )
                        else:
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=GeneralResource(name=instance_id),
                                    status=CheckStatus.UNKNOWN,
                                    summary=f"Failed to check interactive access for EC2 instance {instance_id}.",
                                    exception=str(e)
                                )
                            )
        except Exception as e:
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="EC2"),
                    status=CheckStatus.UNKNOWN,
                    summary="Unexpected error during interactive access check execution.",
                    exception=str(e)
                )
            )
            
        return report
