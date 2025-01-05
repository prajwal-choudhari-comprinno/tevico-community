"""
AUTHOR: RONIT CHAUHAN
EMAIL: ronit.chauhan@comprinno.net
DATE: 2024-1-4
"""

"""
Check: Ensures that Application Load Balancers (ALBs) are protected by WAF Web ACL
Compliance Status: 
    PASS: ALB is protected by WAF Web ACL
    FAIL: ALB is not protected by WAF Web ACL or no ALBs found
"""

import boto3
from typing import Dict, Tuple
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class elb_waf_acl_attached(Check):
    def _check_waf_association(self, wafv2_client, lb_arn: str) -> Tuple[bool, str]:
        """
        Checks if an ALB has WAFv2 Web ACL attached
        
        Args:
            wafv2_client: boto3 WAFv2 client
            lb_arn: ARN of the load balancer
            
        Returns:
            tuple: (is_protected, status_message)
        """
        try:
            response = wafv2_client.get_web_acl_for_resource(
                ResourceArn=lb_arn
            )
            
            if 'WebACL' in response:
                web_acl_name = response['WebACL']['Name']
                return True, f"ELBv2 ALB is protected by WAFv2 Web ACL {web_acl_name}"
            
            return False, "ELBv2 ALB is not protected by WAFv2 Web ACL"
            
        except wafv2_client.exceptions.WAFNonexistentItemException:
            return False, "ELBv2 ALB is not protected by WAFv2 Web ACL"
        except ClientError:
            return False, "Failed to check WAF association"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Executes the ALB WAF Web ACL association check
        
        Args:
            connection: boto3 Session object
            
        Returns:
            CheckReport: Results of the security check
        """
        try:
            report = CheckReport(name=__name__)
            report.passed = True
            
            elbv2_client = connection.client('elbv2')
            wafv2_client = connection.client('wafv2')
            
            alb_found = False
            
            try:
                paginator = elbv2_client.get_paginator('describe_load_balancers')
                
                for page in paginator.paginate():
                    load_balancers = page.get('LoadBalancers', [])
                    
                    for lb in load_balancers:
                        # Check if it's an ALB
                        if lb.get('Type', '').lower() == 'application':
                            alb_found = True
                            lb_name = lb['LoadBalancerName']
                            lb_arn = lb['LoadBalancerArn']
                            
                            # Check WAF association
                            is_protected, status_message = self._check_waf_association(
                                wafv2_client, lb_arn
                            )
                            
                            # Update resource status with message
                            resource_key = f"{lb_name}: {status_message}"
                            report.resource_ids_status[resource_key] = is_protected
                            
                            # If any ALB is not protected, mark overall check as failed
                            if not is_protected:
                                report.passed = False
                
                # If no ALBs were found, mark check as failed
                if not alb_found:
                    report.passed = False
                    report.resource_ids_status["No ALB Found"] = False
                    
            except ClientError as e:
                report.passed = False
                report.resource_ids_status["Error: Failed to list ALBs"] = False
                
        except Exception as e:
            report.passed = False
            report.resource_ids_status["Error: Unexpected error occurred"] = False
            
        return report
