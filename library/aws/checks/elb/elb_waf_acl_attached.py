"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-10
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class elb_waf_acl_attached(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            client = connection.client('elbv2')
            waf_client = connection.client('wafv2')
            paginator = client.get_paginator('describe_load_balancers')
            account_id = connection.client('sts').get_caller_identity()['Account']
            region = client.meta.region_name

            for page in paginator.paginate():
                load_balancers = page['LoadBalancers']
                for lb in load_balancers:
                    lb_arn = lb['LoadBalancerArn']
                    lb_name = lb['LoadBalancerName']
                    resource = AwsResource(arn=lb_arn)

                    try:
                        waf_association = waf_client.get_web_acl_for_resource(ResourceArn=lb_arn)
                        waf_attached = 'WebACL' in waf_association

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED if waf_attached else CheckStatus.FAILED,
                                summary=f"WAF ACL {'attached' if waf_attached else 'not attached'} to {lb_name}."
                            )
                        )
                        if not waf_attached:
                            report.status = CheckStatus.FAILED
                    
                    except waf_client.exceptions.WAFNonexistentItemException:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"No WAF ACL attached to {lb_name}."
                            )
                        )
                        report.status = CheckStatus.FAILED
                    except Exception as e:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Error checking WAF ACL for {lb_name}: {str(e)}"
                            )
                        )
                        report.status = CheckStatus.FAILED
        
        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="ELB"),
                    status=CheckStatus.FAILED,
                    summary=f"Error retrieving load balancers: {str(e)}"
                )
            )
        
        return report
