"""
AUTHOR: deepak.puri@comprinno.net
DATE: 09-10-2024
"""
import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class ec2_network_acl_allow_ingress_any_port(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('ec2')
        acls = client.describe_network_acls()['NetworkAcls']
        
        report.passed = True

        for acl in acls:
            acl_id = acl['NetworkAclId']
            acl_allows_ingress = False
            
            for entry in acl['Entries']:
                if entry['Egress'] is False: 
                    if entry['RuleAction'] == 'allow' and entry['CidrBlock'] == '0.0.0.0/0':  
                        port_range = entry.get('PortRange')
                        if port_range and port_range['From'] == 0 and port_range['To'] == 65535:  # All network ports
                            acl_allows_ingress = True
                            break  
                        if entry['Protocol'] == '-1':  
                            acl_allows_ingress = True
                            break  
            
            if acl_allows_ingress:
                report.passed = False  
                report.resource_ids_status[acl_id] = False
            else:
                report.resource_ids_status[acl_id] = True
                
        return report
