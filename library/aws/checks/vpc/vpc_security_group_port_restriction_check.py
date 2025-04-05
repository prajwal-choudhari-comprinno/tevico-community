"""
AUTHOR: Prajwal G
EMAIL: prajwal.govindraja@comprinno.net
DATE: 2024-05-05
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, GeneralResource, CheckReport, CheckStatus, ResourceStatus
from tevico.engine.entities.check.check import Check

# Define the check class for VPC Security Group Port Restrictions
class vpc_security_group_port_restriction_check(Check):
    # This method performs the check and returns a report.
    def execute(self, connection: boto3.Session) -> CheckReport:
        # Initialize the check report with a default status of PASSED.
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize AWS clients for EC2 and STS
            ec2_client = connection.client('ec2')
            sts_client = connection.client('sts')
            
            # Retrieve the AWS account ID and region for constructing valid ARNs
            account_id = sts_client.get_caller_identity()['Account']
            region = ec2_client.meta.region_name

            # Retrieve all security groups using pagination
            security_groups = []
            next_token = None
            while True:
                if next_token:
                    response = ec2_client.describe_security_groups(NextToken=next_token)
                else:
                    response = ec2_client.describe_security_groups()
                security_groups.extend(response.get("SecurityGroups", []))
                next_token = response.get("NextToken")
                if not next_token:
                    break

            # If no security groups are found, mark the check as NOT_APPLICABLE and return the report.
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

            # Define the set of sensitive ports to check (SSH, HTTP, HTTPS)
            restricted_ports = {22, 80, 443}

            # Iterate over each security group to evaluate its rules
            for sg in security_groups:
                group_id = sg.get("GroupId")
                # Construct a valid ARN for the security group
                sg_arn = f"arn:aws:ec2:{region}:{account_id}:security-group/{group_id}"
                resource = AwsResource(arn=sg_arn)

                try:
                    # Retrieve inbound and outbound rules
                    inbound = sg.get("IpPermissions", [])
                    outbound = sg.get("IpPermissionsEgress", [])
                    all_rules = inbound + outbound
                    failed = False
                    summary = ""

                    # Loop through each rule to check for unrestricted access on sensitive ports
                    for rule in all_rules:
                        from_port = rule.get("FromPort")
                        to_port = rule.get("ToPort")
                        # Check if the rule targets one of the sensitive ports
                        if (from_port in restricted_ports) or (to_port in restricted_ports):
                            ip_ranges = rule.get("IpRanges", [])
                            ipv6_ranges = rule.get("Ipv6Ranges", [])
                            # If the rule allows access from any IPv4 or IPv6 address, flag it as a failure
                            if any(r.get("CidrIp") == "0.0.0.0/0" for r in ip_ranges) or \
                               any(r.get("CidrIpv6") == "::/0" for r in ipv6_ranges):
                                failed = True
                                # Choose the port that is restricted
                                port = from_port if from_port in restricted_ports else to_port
                                summary = f"Security group {group_id} has open access on restricted port {port}."
                                break

                    # Update the report based on the result for this security group
                    if failed:
                        report.status = CheckStatus.FAILED
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
                                summary=f"Security group {group_id} restricts access to sensitive ports."
                            )
                        )
                except Exception as e:
                    # If an error occurs while processing a security group, mark its status as UNKNOWN
                    report.status = CheckStatus.UNKNOWN
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.UNKNOWN,
                            summary=f"Error processing security group {group_id}: {str(e)}",
                            exception=str(e)
                        )
                    )
        except Exception as e:
            # If an error occurs while listing security groups, mark the overall check as UNKNOWN
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary=f"Error listing security groups: {str(e)}",
                    exception=str(e)
                )
            )

        # Return the final report after processing all security groups.
        return report
