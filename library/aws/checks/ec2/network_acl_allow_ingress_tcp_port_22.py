"""
AUTHOR: deepak.puri@comprinno.net
DATE: 09-10-2024
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class network_acl_allow_ingress_tcp_port_22(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('ec2')
        acls = client.describe_network_acls()['NetworkAcls']
        
        tcp_protocol = "6"  # Protocol number for TCP
        check_port = 22  # SSH port
        
        for acl in acls:
            acl_id = acl['NetworkAclId']
            acl_allows_ingress = False
            
            for entry in acl['Entries']:
                if entry['Egress'] is False:  # Only check ingress rules
                    if entry['CidrBlock'] == '0.0.0.0/0':  # Check if open to the internet
                        if entry['Protocol'] == tcp_protocol:
                            port_range = entry.get('PortRange')
                            if port_range and port_range['From'] <= check_port <= port_range['To']:
                                acl_allows_ingress = True
                                break  # No need to check further, fail the check
                        if entry['Protocol'] == '-1': # If protocol is '-1', it allows all traffic (protocol all)
                            acl_allows_ingress = True
                            break  # No need to check further, fail the check
            
            if acl_allows_ingress:
                report.passed = False
                report.resource_ids_status[acl_id] = False
            else:
                report.passed = True
                report.resource_ids_status[acl_id] = True
        
        return report
