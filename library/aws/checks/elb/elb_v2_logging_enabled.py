"""
AUTHOR: RONIT CHAUHAN
EMAIL: ronit.chauhan@comprinno.net
DATE: 2024-1-4
"""

"""
Check: Ensures that Application/Network/Gateway Load Balancers (ELBv2) have access logging enabled
Compliance Status: 
    PASS: ELBv2 has access logging enabled and configured to S3
    FAIL: ELBv2 has access logging disabled or no ELBv2 found
"""

import boto3
from typing import Dict, Tuple
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class elb_v2_logging_enabled(Check):
    def _get_lb_type_display(self, lb_type: str) -> str:
        """
        Converts load balancer type to display format
        
        Args:
            lb_type: Type of load balancer (application/network/gateway)
            
        Returns:
            str: Display format of load balancer type
        """
        type_mapping = {
            'application': 'ALB',
            'network': 'NLB',
            'gateway': 'GWLB'
        }
        return type_mapping.get(lb_type.lower(), lb_type.upper())

    def _check_access_logging(self, client, lb_arn: str) -> Tuple[bool, str]:
        """
        Checks if access logging is enabled for an ELBv2
        
        Args:
            client: boto3 ELBv2 client
            lb_arn: ARN of the load balancer
            
        Returns:
            tuple: (is_enabled, status_message)
        """
        try:
            attributes = client.describe_load_balancer_attributes(
                LoadBalancerArn=lb_arn
            )['Attributes']
            
            # Check if access logging is enabled
            for attr in attributes:
                if attr['Key'] == 'access_logs.s3.enabled':
                    is_enabled = attr['Value'].lower() == 'true'
                    return is_enabled, None
                    
            return False, None
            
        except ClientError:
            return False, "Failed to retrieve attributes"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Executes the ELBv2 access logging check
        
        Args:
            connection: boto3 Session object
            
        Returns:
            CheckReport: Results of the security check
        """
        try:
            report = CheckReport(name=__name__)
            report.passed = True
            
            client = connection.client('elbv2')
            
            elbv2_found = False
            
            try:
                paginator = client.get_paginator('describe_load_balancers')
                
                for page in paginator.paginate():
                    load_balancers = page.get('LoadBalancers', [])
                    
                    if load_balancers:
                        elbv2_found = True
                        
                        for lb in load_balancers:
                            lb_name = lb['LoadBalancerName']
                            lb_arn = lb['LoadBalancerArn']
                            lb_type = self._get_lb_type_display(lb['Type'])
                            
                            # Check access logging status
                            is_enabled, error_message = self._check_access_logging(
                                client, lb_arn
                            )
                            
                            if error_message:
                                resource_key = f"{lb_name}: {error_message}"
                                report.resource_ids_status[resource_key] = False
                                report.passed = False
                                continue
                            
                            # Create status message based on logging status
                            if is_enabled:
                                status_message = f"ELBv2 {lb_type} has access logs to S3 configured"
                            else:
                                status_message = f"ELBv2 {lb_type} does not have access logs configured"
                            
                            # Update resource status with message
                            resource_key = f"{lb_name}: {status_message}"
                            report.resource_ids_status[resource_key] = is_enabled
                            
                            # If any ELBv2 fails, mark overall check as failed
                            if not is_enabled:
                                report.passed = False
                
                # If no ELBv2s were found, mark check as failed
                if not elbv2_found:
                    report.passed = False
                    report.resource_ids_status["No ELBv2 Found"] = False
                    
            except ClientError as e:
                report.passed = False
                report.resource_ids_status["Error: Failed to list ELBv2s"] = False
                
        except Exception as e:
            report.passed = False
            report.resource_ids_status["Error: Unexpected error occurred"] = False
            
        return report
