"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-12-24

Description: This script checks if Classic Load Balancers are using secure connections (HTTPS/SSL/TLS).
Think of it like a security inspector checking if all doors have proper locks installed.
If a load balancer isn't using secure protocols, it's like having an unlocked door - unsafe!
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
import logging
from botocore.exceptions import (
    ClientError,          # Handles AWS-specific errors
    EndpointConnectionError,  # Handles network connection issues
    NoCredentialsError,   # Handles missing AWS credentials
    ParamValidationError  # Handles invalid parameter errors
)

# Setup logging to track what's happening in the code
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class elb_ssl_listeners_enabled(Check):
    """
    Security check for Classic Load Balancers to ensure they use secure protocols.
    Like checking if all entrance doors have proper security locks installed.
    """

    def check_ssl_policy(self, client, lb_name: str, port: int) -> tuple:
        """
        Checks if a specific port on a load balancer uses secure protocols.
        
        Think of this like checking a specific door's lock:
        - If it has a secure lock (HTTPS/SSL) = Good ✅
        - If it has no lock (HTTP) = Bad ❌

        Args:
            client: Our connection to AWS (like a security badge)
            lb_name: Name of the load balancer (building) we're checking
            port: The specific port (door) we're checking

        Returns:
            Two pieces of information:
            1. Is it secure? (True/False)
            2. What's the status message?
        """
        try:
            # Get the security policy details
            policies = client.describe_load_balancer_policies(
                LoadBalancerName=lb_name
            )['PolicyDescriptions']
            
            # Check if the security policy is adequate (like checking if the lock is strong enough)
            for policy in policies:
                if policy.get('PolicyTypeName') == 'SSLNegotiationPolicyType':
                    logger.info(f"✅ Checking security policy for {lb_name} on port {port}")
                    return True
            return False

        except ClientError as e:
            # Handle AWS-specific errors
            logger.error(f"🚫 Error checking SSL policy for '{lb_name}': {e.response['Error']['Message']}")
            return False
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"❌ Unexpected error checking SSL policy for '{lb_name}': {str(e)}")
            return False

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main method that checks all load balancers for secure protocols.
        
        Think of this like doing a complete security audit of a building:
        1. Check all entrances (listeners)
        2. Verify each door has proper locks (secure protocols)
        3. Create a report of what we found
        
        Returns:
            A report card showing which load balancers are secure
        """
        # Initialize our report card
        report = CheckReport(name=__name__)
        report.passed = True  # Start optimistic - assume everything is secure
        report.resource_ids_status = {}  # Will store results for each load balancer
        found_load_balancers = False

        try:
            # Connect to AWS ELB service
            elb_client = connection.client('elb')
            
            try:
                # Get list of all load balancers (like getting a list of all buildings to inspect)
                classic_lbs = elb_client.describe_load_balancers()['LoadBalancerDescriptions']
                
                if classic_lbs:
                    found_load_balancers = True
                    
                    # Check each load balancer
                    for lb in classic_lbs:
                        lb_name = lb['LoadBalancerName']
                        has_secure_listener = False

                        # Check each listener (door) on the load balancer
                        for listener in lb['ListenerDescriptions']:
                            port = listener['Listener']['LoadBalancerPort']
                            protocol = listener['Listener']['Protocol'].upper()

                            # Check if using secure protocols (HTTPS/SSL)
                            if protocol in ['HTTPS', 'SSL']:
                                is_secure = self.check_ssl_policy(elb_client, lb_name, port)
                                has_secure_listener = has_secure_listener or is_secure

                        # Record the results
                        resource_key = f"CLB:{lb_name}"
                        report.resource_ids_status[resource_key] = has_secure_listener

                        if not has_secure_listener:
                            report.passed = False
                            logger.info(f"⚠️ Load balancer '{lb_name}' is not using secure protocols!")

                # Handle case where no load balancers were found
                if not found_load_balancers:
                    report.passed = False
                    report.resource_ids_status["No Load Balancers Found"] = False
                    logger.warning("ℹ️ No Classic Load Balancers found to check")

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
