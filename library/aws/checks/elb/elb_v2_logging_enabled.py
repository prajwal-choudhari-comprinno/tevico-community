"""
AUTHOR: Deepak Puri
EMAIL: deepak.puri@comprinno.net
DATE: 2025-01-24
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, AwsResource, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class elb_v2_logging_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        # Initialize the report
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        # Initialize the ELBv2 client
        client = connection.client('elbv2')

        try:
            # Pagination to get all load balancers
            load_balancers = []
            next_token = None

            while True:
                response = client.describe_load_balancers(Marker=next_token) if next_token else client.describe_load_balancers()
                load_balancers.extend(response.get('LoadBalancers', []))
                next_token = response.get('NextMarker', None)

                if not next_token:
                    break

            # Iterate over all load balancers and check logging status
            for lb in load_balancers:
                lb_name = lb['LoadBalancerName']  # Extract ALB name
                lb_arn = lb['LoadBalancerArn']

                # Get ELBv2 attributes to check logging
                attributes = client.describe_load_balancer_attributes(LoadBalancerArn=lb['LoadBalancerArn'])['Attributes']

                # Check if access logging is enabled
                logging_enabled = any(
                    attr['Key'] == 'access_logs.s3.enabled' and attr['Value'] == 'true'
                    for attr in attributes
                )

                # Record the result for this load balancer using ALB name
                if logging_enabled:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=lb_arn),
                            status=CheckStatus.PASSED,
                            summary=f"{lb_name} has logging enabled."
                        )
                    )
                else:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=AwsResource(arn=lb_arn),
                            status=CheckStatus.FAILED,
                            summary=f"{lb_name} has logging not enabled."
                        )
                    )

        except Exception as e:
            # Handle unexpected errors
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error fetching load balancers.",
                    exception=str(e)
                )
            )
            report.status = CheckStatus.FAILED

        return report
