"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-12-24

Description: This script checks if Application Load Balancers (ALBs) have Web Application Firewall (WAF) protection.
Think of it like checking if buildings have security guards at their entrances.
WAF is like a security guard that protects your web applications from cyber attacks.
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
import logging
from botocore.exceptions import (
    ClientError,            # For AWS service-specific errors
    EndpointConnectionError,  # For network connectivity issues
    NoCredentialsError,     # For missing AWS credentials
    ParamValidationError    # For invalid parameter errors
)

# Setup logging to track what's happening
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class elb_waf_acl_attached(Check):
    """
    Security check for Application Load Balancers to ensure WAF protection is enabled.
    Like making sure each building entrance has a security guard on duty.
    """

    def check_waf_protection(self, client_wafv2, client_waf_regional, alb_arn: str, alb_name: str) -> tuple:
        """
        Checks if a specific load balancer has WAF protection.

        Think of this like checking if a specific entrance has a security guard:
        - If there's a guard (WAF enabled) = Good ✅
        - If there's no guard (WAF disabled) = Bad ❌

        Args:
            client_wafv2: Connection to new WAF service (like head security office)
            client_waf_regional: Connection to old WAF service (like local security office)
            alb_arn: The unique ID of the load balancer
            alb_name: The friendly name of the load balancer

        Returns:
            Two pieces of information:
            1. Is it protected? (True/False)
            2. What type of protection it has
        """
        try:
            # Check new WAF protection (WAFv2)
            try:
                wafv2_response = client_wafv2.get_web_acl_for_resource(ResourceArn=alb_arn)
                if 'WebACL' in wafv2_response:
                    return True, "Protected by WAFv2"
            except ClientError as e:
                if e.response['Error']['Code'] not in ['ResourceNotFoundException', 'WAFNonexistentItemException']:
                    logger.error(f"⚠️ Error checking WAFv2 for '{alb_name}': {e.response['Error']['Message']}")

            # Check old WAF protection (WAF Classic)
            try:
                waf_response = client_waf_regional.get_web_acl_for_resource(ResourceArn=alb_arn)
                if 'WebACLSummary' in waf_response:
                    return True, "Protected by WAF Classic"
            except ClientError as e:
                if e.response['Error']['Code'] not in ['ResourceNotFoundException', 'WAFNonexistentItemException']:
                    logger.error(f"⚠️ Error checking WAF Classic for '{alb_name}': {e.response['Error']['Message']}")

            return False, "No WAF protection found"

        except Exception as e:
            # Handle unexpected errors
            logger.error(f"❌ Unexpected error checking WAF for '{alb_name}': {str(e)}")
            return False, f"Error: {str(e)}"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main method that checks all Application Load Balancers for WAF protection.

        Think of this like doing a complete security audit of all buildings:
        1. Find all entrances (load balancers)
        2. Check if each entrance has a security guard (WAF)
        3. Create a report of what we found

        Returns:
            A report card showing which load balancers are protected
        """
        # Initialize our report card
        report = CheckReport(name=__name__)
        report.passed = True  # Start optimistic - assume everything is protected
        report.resource_ids_status = {}  # Will store results for each load balancer
        found_albs = False

        try:
            # Create connections to AWS services
            elbv2_client = connection.client('elbv2')
            wafv2_client = connection.client('wafv2')
            waf_regional_client = connection.client('waf-regional')

            try:
                # Get list of all load balancers
                paginator = elbv2_client.get_paginator('describe_load_balancers')
                
                for page in paginator.paginate():
                    # Check each load balancer
                    for lb in page['LoadBalancers']:
                        # Only check Application Load Balancers
                        if lb['Type'].lower() != 'application':
                            continue

                        found_albs = True
                        lb_arn = lb['LoadBalancerArn']
                        lb_name = lb['LoadBalancerName']

                        # Check if this ALB has WAF protection
                        is_protected, protection_type = self.check_waf_protection(
                            wafv2_client, waf_regional_client, lb_arn, lb_name
                        )

                        # Record the results
                        resource_key = f"ALB:{lb_name}"
                        report.resource_ids_status[resource_key] = is_protected

                        if not is_protected:
                            report.passed = False
                            logger.warning(f"🚨 Alert: Load balancer '{lb_name}' has no WAF protection!")
                        else:
                            logger.info(f"✅ Load balancer '{lb_name}' is protected: {protection_type}")

                # Handle case where no Application Load Balancers were found
                if not found_albs:
                    report.passed = False
                    report.resource_ids_status["No Application Load Balancers Found"] = False
                    logger.warning("ℹ️ No Application Load Balancers found to check")

            except ClientError as e:
                # Handle AWS API errors
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDenied':
                    logger.error("🔒 Access denied - check your permissions")
                else:
                    logger.error(f"⚠️ Error listing load balancers: {e.response['Error']['Message']}")
                report.passed = False
                report.resource_ids_status["Error"] = False

            except ParamValidationError as e:
                # Handle invalid parameter errors
                logger.error(f"📝 Invalid parameter error: {str(e)}")
                report.passed = False
                report.resource_ids_status["Parameter Error"] = False

        except NoCredentialsError:
            # Handle missing AWS credentials
            logger.error("🔑 AWS credentials missing - check your AWS configuration")
            report.passed = False
            report.resource_ids_status["No AWS Credentials"] = False
        
        except EndpointConnectionError:
            # Handle AWS connection issues
            logger.error("🌐 Cannot connect to AWS - check your internet connection")
            report.passed = False
            report.resource_ids_status["Connection Error"] = False
        
        except Exception as e:
            # Handle any unexpected errors
            logger.error(f"💥 Critical error in check execution: {str(e)}")
            report.passed = False
            report.resource_ids_status["Error"] = False

        return report
