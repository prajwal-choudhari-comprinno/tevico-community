"""
AUTHOR: Prajwal G
EMAIL: prajwal.govindraja@comprinno.net
DATE: 2024-04-05
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, GeneralResource, CheckReport, CheckStatus, ResourceStatus
from tevico.engine.entities.check.check import Check

class vpc_service_endpoint_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        # Initialize the report with a default PASSED status.
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []
        
        try:
            # Create AWS clients for EC2 and STS.
            ec2_client = connection.client('ec2')
            sts_client = connection.client('sts')
            
            # Retrieve account and region information.
            account_id = sts_client.get_caller_identity()['Account']
            region = ec2_client.meta.region_name
            
            # Retrieve all VPCs.
            vpcs_response = ec2_client.describe_vpcs()
            vpcs = vpcs_response.get("Vpcs", [])
            
            if not vpcs:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No VPCs found in the account."
                    )
                )
                return report

            # Retrieve all VPC endpoints using pagination.
            vpc_endpoints = []
            next_token = None
            while True:
                if next_token:
                    response = ec2_client.describe_vpc_endpoints(NextToken=next_token)
                else:
                    response = ec2_client.describe_vpc_endpoints()
                vpc_endpoints.extend(response.get("VpcEndpoints", []))
                next_token = response.get("NextToken")
                if not next_token:
                    break

            # Group endpoints by VPC ID for faster lookup.
            endpoints_by_vpc = {}
            for endpoint in vpc_endpoints:
                vpc_id = endpoint.get("VpcId")
                if vpc_id:
                    endpoints_by_vpc.setdefault(vpc_id, []).append(endpoint)

            # Evaluate each VPC: Check if at least one associated endpoint is in "available" state.
            for vpc in vpcs:
                vpc_id = vpc.get("VpcId")
                # Construct a proper VPC ARN: arn:aws:ec2:<region>:<account-id>:vpc/<vpc-id>
                vpc_arn = f"arn:aws:ec2:{region}:{account_id}:vpc/{vpc_id}"
                resource = AwsResource(arn=vpc_arn, resource_id=vpc_id)
                
                endpoints = endpoints_by_vpc.get(vpc_id, [])
                available_endpoints = [ep for ep in endpoints if ep.get("State", "").lower() == "available"]
                
                if available_endpoints:
                    summary = (
                        f"VPC {vpc_id} has {len(available_endpoints)} service endpoint(s) "
                        f"that are in the 'available' state, meeting the requirement."
                    )
                    status = CheckStatus.PASSED
                else:
                    summary = (
                        f"VPC {vpc_id} does not have any service endpoints in the 'available' state. "
                        "At least one available endpoint is required."
                    )
                    status = CheckStatus.FAILED
                    # Update overall report status if any VPC fails.
                    report.status = CheckStatus.FAILED

                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=resource,
                        status=status,
                        summary=summary
                    )
                )

        except Exception as e:
            # Global error handling: If an error occurs, mark the check as UNKNOWN.
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary=f"Error retrieving VPCs or endpoints: {str(e)}",
                    exception=str(e)
                )
            )
            
        # Return the final report.
        return report
