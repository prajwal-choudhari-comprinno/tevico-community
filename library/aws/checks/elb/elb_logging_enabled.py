"""
AUTHOR: RONIT CHAUHAN
EMAIL: ronit.chauhan@comprinno.net
DATE: 2024-1-4
"""
"""
Check: Ensures that Classic Load Balancers (ELBs) have access logging enabled
Compliance Status: 
    PASS: ELB has access logging enabled and configured to an S3 bucket
    FAIL: ELB has access logging disabled or no ELBs found
"""
import boto3
from typing import Dict
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class elb_logging_enabled(Check):
    def _check_access_logging(self, client, lb_name: str) -> tuple:
        """
        Checks if access logging is enabled for a specific ELB
        
        Args:
            client: boto3 ELB client
            lb_name: Name of the load balancer
            
        Returns:
            tuple: (is_enabled, status_message)
        """
        try:
            attributes = client.describe_load_balancer_attributes(
                LoadBalancerName=lb_name
            )['LoadBalancerAttributes']
            
            access_log = attributes.get('AccessLog', {})
            is_enabled = access_log.get('Enabled', False)
            
            if is_enabled:
                return True, "ELB has access_logs enabled"
            return False, "ELB access_logs is not configured"
            
        except ClientError:
            return False, "Failed to retrieve ELB attributes"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Executes the ELB access logging check
        
        Args:
            connection: boto3 Session object
            
        Returns:
            CheckReport: Results of the security check
        """
        try:
            report = CheckReport(name=__name__)
            report.passed = True
            
            client = connection.client('elb')
            paginator = client.get_paginator('describe_load_balancers')
            
            load_balancers_found = False
            
            try:
                for page in paginator.paginate():
                    load_balancers = page.get('LoadBalancerDescriptions', [])
                    
                    if load_balancers:
                        load_balancers_found = True
                        
                        for lb in load_balancers:
                            lb_name = lb['LoadBalancerName']
                            
                            # Check access logging status
                            is_enabled, status_message = self._check_access_logging(
                                client, lb_name
                            )
                            
                            # Update resource status with message
                            resource_key = f"{lb_name}: {status_message}"
                            report.resource_ids_status[resource_key] = is_enabled
                            
                            # If any ELB fails, mark overall check as failed
                            if not is_enabled:
                                report.passed = False
                    
                # If no load balancers were found, mark check as failed
                if not load_balancers_found:
                    report.passed = False
                    report.resource_ids_status["No ELB Found"] = False
                    
            except ClientError as e:
                report.passed = False
                report.resource_ids_status["Error: Failed to list ELBs"] = False
                
        except Exception as e:
            report.passed = False
            report.resource_ids_status["Error: Unexpected error occurred"] = False
            
        return report
