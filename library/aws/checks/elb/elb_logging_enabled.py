"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-10
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class elb_logging_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []
        
        try:
            client = connection.client('elb')
            paginator = client.get_paginator('describe_load_balancers')
            account_id = connection.client('sts').get_caller_identity()['Account']
            region = client.meta.region_name

            # Iterate over all ELBs
            for page in paginator.paginate():
                load_balancers = page['LoadBalancerDescriptions']
                for lb in load_balancers:
                    lb_name = lb.get('LoadBalancerName', "N/A")
                    lb_arn = lb.get('LoadBalancerArn', f"arn:aws:elasticloadbalancing:{region}:{account_id}:loadbalancer/{lb_name}")
                    resource = AwsResource(arn=lb_arn)
                    
                    try:
                        lb_attributes = client.describe_load_balancer_attributes(LoadBalancerName=lb_name)['LoadBalancerAttributes']
                        access_logs = lb_attributes.get('AccessLog', {})
                        logging_enabled = access_logs.get('Enabled', False)
                        
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED if logging_enabled else CheckStatus.FAILED,
                                summary=f"Access logging {'enabled' if logging_enabled else 'not enabled'} for ELB {lb_name}."
                            )
                        )
                        if not logging_enabled:
                            report.status = CheckStatus.FAILED
                    
                    except Exception as e:
                        report.status = CheckStatus.FAILED
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Error checking logging for ELB {lb_name}: {str(e)}"
                            )
                        )

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing ELB data: {str(e)}"
                )
            )

        return report
