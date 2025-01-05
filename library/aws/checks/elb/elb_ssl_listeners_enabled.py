"""
AUTHOR: RONIT CHAUHAN
EMAIL: ronit.chauhan@comprinno.net
DATE: 2024-1-4
"""
"""
Check: Ensures that all Classic Load Balancers (ELBs) use secure protocols (HTTPS/SSL) for their listeners
Compliance Status: 
    PASS: All listeners use secure protocols (HTTPS/SSL)
    FAIL: One or more listeners use insecure protocols or no listeners found
"""

import boto3
from typing import Dict, List
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class elb_ssl_listeners_enabled(Check):
    def _evaluate_listener(self, listener: Dict) -> tuple:
        """
        Evaluates if a single listener uses secure protocol
        
        Args:
            listener: Single listener configuration
            
        Returns:
            tuple: (is_secure, status_message)
        """
        protocol = listener['Protocol']
        port = listener['LoadBalancerPort']
        
        if protocol in ('HTTPS', 'SSL'):
            return True, f"ELB Listener {protocol}:{port} uses secure protocol {protocol}"
        return False, f"ELB Listener {protocol}:{port} uses insecure protocol {protocol}"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Executes the ELB SSL listeners security check
        
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
                            listeners = lb.get('ListenerDescriptions', [])
                            
                            if not listeners:
                                resource_key = f"{lb_name}: No listeners found"
                                report.resource_ids_status[resource_key] = False
                                report.passed = False
                                continue
                            
                            # Evaluate each listener separately
                            for listener_desc in listeners:
                                listener = listener_desc['Listener']
                                is_secure, status_message = self._evaluate_listener(listener)
                                
                                # Update resource status with message for each listener
                                resource_key = f"{lb_name}: {status_message}"
                                report.resource_ids_status[resource_key] = is_secure
                                
                                # If any listener is insecure, mark overall check as failed
                                if not is_secure:
                                    report.passed = False
                
                # If no load balancers were found, mark check as failed
                if not load_balancers_found:
                    report.passed = False
                    report.resource_ids_status["No ELB Found"] = False
                    
            except ClientError as e:
                report.passed = False
                report.resource_ids_status["Error"] = False
                
        except Exception as e:
            report.passed = False
            report.resource_ids_status["Error"] = False
            
        return report
