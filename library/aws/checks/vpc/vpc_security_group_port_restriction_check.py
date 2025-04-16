"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-04-15
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import GeneralResource, CheckReport, CheckStatus, ResourceStatus
from tevico.engine.entities.check.check import Check

class vpc_security_group_port_restriction_check(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        
        # Initialize the check report.
        
        report = CheckReport(name=__name__)
        report.resource_ids_status = []

        try:
            
            # Sets up AWS clients for EC2 to retrieve security groups.
            
            ec2_client = connection.client('ec2')
            
            
            # Retrieves All Security Groups Using Pagination.
            
            security_groups = []
            paginator = ec2_client.get_paginator('describe_security_groups')
            for page in paginator.paginate():
                security_groups.extend(page.get("SecurityGroups", []))

            
            # Handles Case Where No Security Groups Are Found.
            
            if not security_groups:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No security groups found."
                    )
                )
                return report

            
            # These are the ports to check for unrestricted (public) access.
            restricted_ports = {
                            20, 21,  # FTP
                            22,      # SSH
                            23,      # Telnet
                            25,      # SMTP
                            110,     # POP3
                            135,     # RPC
                            143,     # IMAP
                            445,     # SMB
                            1433, 1434,  # SQL Server
                            3000,    # Development servers
                            3306,    # MySQL
                            3389,    # RDP
                            4333,
                            5000,    # Various applications
                            5432,    # PostgreSQL
                            5500,
                            5601,    # Kibana
                            8080, 8088, 8888,  # Alternative HTTP ports
                            9200, 9300  # Elasticsearch
                        }

            
            # Iterates Over Each Security Group to Evaluate Its Rules.
            
            for sg in security_groups:
                group_id = sg.get("GroupId")
                group_name = sg.get("GroupName", "")
                
                # Security groups don't have traditional ARNs, use the ID as resource identifier
                resource = GeneralResource(name=group_id)

                
                # Retrieves Inbound Rules.
                inbound = sg.get("IpPermissions", [])
                
                # Track violations for this security group
                violations = []
                
                
                # Check inbound rules for unrestricted access to sensitive ports
                for rule in inbound:
                    # Handle rules with port ranges
                    from_port = rule.get("FromPort")
                    to_port = rule.get("ToPort")
                    
                    # Skip rules without port information (e.g., ICMP rules)
                    if from_port is None or to_port is None:
                        continue
                    
                    # Check if any port in the range overlaps with restricted ports
                    # Using any() to avoid nested loop
                    has_restricted_port = any(from_port <= port <= to_port for port in restricted_ports)
                    
                    if not has_restricted_port:
                        continue
                    
                    # Check for public access (0.0.0.0/0 or ::/0)
                    ip_ranges = rule.get("IpRanges", [])
                    ipv6_ranges = rule.get("Ipv6Ranges", [])
                    
                    public_ipv4 = any(r.get("CidrIp") == "0.0.0.0/0" for r in ip_ranges)
                    public_ipv6 = any(r.get("CidrIpv6") == "::/0" for r in ipv6_ranges)
                    
                    if public_ipv4 or public_ipv6:
                        port_range = f"{from_port}-{to_port}" if from_port != to_port else str(from_port)
                        cidr = "0.0.0.0/0" if public_ipv4 else "::/0"
                        violations.append(f"Inbound rule allows {cidr} access to port(s) {port_range}")
                
                
                # Records the Evaluation Result for This Security Group.
                if violations:
                    summary = f"Security group {group_id} ({group_name}) has unrestricted access to sensitive ports:\n"
                    summary += "\n".join(f"- {v}" for v in violations)
                    
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=summary
                        )
                    )
                else:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.PASSED,
                            summary=f"Security group {group_id} ({group_name}) properly restricts access to sensitive ports."
                        )
                    )
                
        except (BotoCoreError, ClientError) as e:
            # AWS API Exception Handling.
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary=f"AWS API request failed. Unable to verify security group configurations: {str(e)}",
                    exception=str(e)
                )
            )
        except Exception as e:
            # Global Exception Handling.
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary=f"Error checking security group configurations: {str(e)}",
                    exception=str(e)
                )
            )

        return report
