"""
AUTHOR: Prajwal G
EMAIL: prajwal.govindraja@comprinno.net
DATE: 2024-04-05
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, GeneralResource, CheckReport, CheckStatus, ResourceStatus
from tevico.engine.entities.check.check import Check

class vpc_flowlogs_traffic_inspection(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        # -------------------------------------------------------------------
        # Initialize the check report.
        # -------------------------------------------------------------------
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # -------------------------------------------------------------------
            # Set up AWS clients for EC2 and STS.
            # EC2 client: to retrieve VPCs and flow logs.
            # STS client: to retrieve account information.
            # -------------------------------------------------------------------
            ec2_client = connection.client('ec2')
            sts_client = connection.client('sts')

            # -------------------------------------------------------------------
            # Retrieves AWS account ID and region.
            # These values are used for constructing valid ARNs.
            # -------------------------------------------------------------------
            account_id = sts_client.get_caller_identity()['Account']
            region = ec2_client.meta.region_name

            # -------------------------------------------------------------------
            # Retrieves all VPCs in the account using pagination.
            # -------------------------------------------------------------------
            vpcs = []
            next_token = None
            while True:
                if next_token:
                    response = ec2_client.describe_vpcs(NextToken=next_token)
                else:
                    response = ec2_client.describe_vpcs()
                vpcs.extend(response.get("Vpcs", []))
                next_token = response.get("NextToken")
                if not next_token:
                    break

            # -------------------------------------------------------------------
            # If no VPCs are found, marks the check as NOT_APPLICABLE and return.
            # -------------------------------------------------------------------
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

            # -------------------------------------------------------------------
            # For each VPC, evaluates whether it has an active flow log enabled.
            # -------------------------------------------------------------------
            for vpc in vpcs:
                vpc_id = vpc.get("VpcId")
                vpc_arn = f"arn:aws:ec2:{region}:{account_id}:vpc/{vpc_id}"
                resource = AwsResource(arn=vpc_arn, resource_id=vpc_id)

                # -------------------------------------------------------------------
                # Retrieves flow logs for the current VPC using pagination.
                # Uses a filter on 'resource-id' to only get logs for this VPC.
                # -------------------------------------------------------------------
                flow_logs = []
                next_token_fl = None
                while True:
                    if next_token_fl:
                        response = ec2_client.describe_flow_logs(
                            Filters=[
                                {'Name': 'resource-id', 'Values': [vpc_id]}
                            ],
                            NextToken=next_token_fl
                        )
                    else:
                        response = ec2_client.describe_flow_logs(
                            Filters=[
                                {'Name': 'resource-id', 'Values': [vpc_id]}
                            ]
                        )
                    flow_logs.extend(response.get("FlowLogs", []))
                    next_token_fl = response.get("NextToken")
                    if not next_token_fl:
                        break

                # -------------------------------------------------------------------
                # Determines which flow logs are active.
                # An active flow log should have FlowLogStatus set to "ACTIVE".
                # -------------------------------------------------------------------
                active_flow_logs = [fl for fl in flow_logs if fl.get("FlowLogStatus", "").upper() == "ACTIVE"]

                # -------------------------------------------------------------------
                # Constructs a summary and determine the status for this VPC.
                # -------------------------------------------------------------------
                if active_flow_logs:
                    summary = (
                        f"VPC {vpc_id} has {len(active_flow_logs)} active flow log(s) enabled for traffic inspection."
                    )
                    status = CheckStatus.PASSED
                else:
                    summary = (
                        f"VPC {vpc_id} does not have any active flow logs enabled for traffic inspection."
                    )
                    status = CheckStatus.FAILED
                    # Updates overall report status to FAILED if any VPC fails the check.
                    report.status = CheckStatus.FAILED

                # -------------------------------------------------------------------
                # Appends the result for this VPC to the report.
                # -------------------------------------------------------------------
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=resource,
                        status=status,
                        summary=summary
                    )
                )
                
        except Exception as e:
            # -------------------------------------------------------------------
            # Global exception handling:
            # If an error occurs during processing, mark the check as UNKNOWN
            # and record the error details.
            # -------------------------------------------------------------------
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary=f"Error retrieving VPCs or flow logs: {str(e)}",
                    exception=str(e)
                )
            )

        return report