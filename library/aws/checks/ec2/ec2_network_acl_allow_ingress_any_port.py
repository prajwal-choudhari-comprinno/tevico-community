"""
AUTHOR: Deepak Puri
EMAIL: deepak.puri@comprinno.net
DATE: 2024-10-09
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, ResourceStatus
from tevico.engine.entities.check.check import Check

class ec2_network_acl_allow_ingress_any_port(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('ec2')
        sts_client = connection.client('sts')
        account_number = sts_client.get_caller_identity()['Account']
        acls = client.describe_network_acls()['NetworkAcls']
        
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        for acl in acls:
            acl_id = acl['NetworkAclId']
            acl_arn = acl.get('NetworkAclArn', f"arn:aws:ec2:{client.meta.region_name}:{account_number}:network-acl/{acl_id}")
            resource = AwsResource(arn=acl_arn)
            acl_allows_ingress = False
            
            for entry in acl['Entries']:
                if entry['Egress']:  
                    continue
                if entry['RuleAction'] != 'allow' or entry['CidrBlock'] != '0.0.0.0/0':  
                    continue
                
                port_range = entry.get('PortRange')
                if port_range and port_range['From'] == 0 and port_range['To'] == 65535:  # All network ports
                    acl_allows_ingress = True
                    break
                if entry['Protocol'] == '-1':  
                    acl_allows_ingress = True
                    break
            
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=resource,
                    status=CheckStatus.FAILED if acl_allows_ingress else CheckStatus.PASSED,
                    summary=f"Network ACL {acl_id} allows ingress on all ports." if acl_allows_ingress else f"Network ACL {acl_id} does not allow ingress on all ports."
                )
            )
            if acl_allows_ingress:
                report.status = CheckStatus.FAILED
        
        return report
