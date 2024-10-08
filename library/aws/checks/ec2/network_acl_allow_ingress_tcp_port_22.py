# """
# AUTHOR: deepak.puri@comprinno.net
# DATE: 09-10-2024
# """

# import boto3

# from tevico.engine.entities.report.check_model import CheckReport
# from tevico.engine.entities.check.check import Check


# class network_acl_allow_ingress_tcp_port_22(Check):

#     def execute(self, connection: boto3.Session) -> CheckReport:
#         report = CheckReport(name=__name__)
#         client = connection.client('ec2')
#         acls = client.describe_network_acls()['NetworkAcls']
        
#         tcp_protocol = "6"  # Protocol number for TCP
#         check_port = 22  # SSH port
        
#         for acl in acls:
#             acl_id = acl['NetworkAclId']
#             print("checking:", acl_id )#debug
#             # Initialize as passed; assume no open port until checked
#             acl_allows_ingress = False
            
#             # Check each entry in the ACL
#             for entry in acl['Entries']:
#                 if entry['Egress'] is False:  # Only check ingress rules
#                     if entry['Protocol'] == tcp_protocol:  # Check if it's a TCP rule
#                         port_range = entry.get('PortRange')
#                         # Check if rule includes port 22
#                         if port_range and port_range['From'] <= check_port <= port_range['To']:
#                             # If the rule allows ingress and is open to the internet
#                             if entry['RuleAction'] == 'allow' and entry['CidrBlock'] == '0.0.0.0/0':
#                                 acl_allows_ingress = True
#                                 print("true")#ddebug
#                                 break  # No need to check further, fail the check

#             # Record the result for the ACL
#             if acl_allows_ingress:
#                 report.passed = False
#                 report.resource_ids_status[acl_id] = False
#             else:
#                 report.passed = True
#                 report.resource_ids_status[acl_id] = True
        
#         return report

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
