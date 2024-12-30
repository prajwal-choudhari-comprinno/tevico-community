"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-12-24

Description: This script checks if Elastic Load Balancers (ELB) have logging enabled.
Think of it like a security system that ensures all visitor logs are being recorded in a building.
If logging is disabled, it's like having security cameras turned off - you can't track who accessed what.
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
import logging
from botocore.exceptions import (
    ClientError,          # Handles AWS-specific errors (like permissions, invalid inputs)
    EndpointConnectionError,  # Handles connection issues to AWS
    NoCredentialsError,   # Handles missing AWS credentials
    ParamValidationError  # Handles invalid parameter errors
)

# Setup logging to track what's happening in the code
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class elb_logging_enabled(Check):
    """
    Security check for Elastic Load Balancers to ensure logging is enabled.
    
    This is like having a security guard checking if all security cameras are recording.
    If any camera (load balancer) isn't recording (logging), it's flagged as a security risk.
    """

    def check_logging_enabled(self, client, lb_name: str) -> tuple:
        """
        Checks if a specific load balancer has logging turned on.
        
        Think of this like checking if a specific security camera is recording:
        - If it's recording (logging enabled) = Good ✅
        - If it's not recording (logging disabled) = Bad ❌

        Args:
            client: Our connection to AWS (like a security badge)
            lb_name: The name of the load balancer we're checking

        Returns:
            Two pieces of information:
            1. Is it secure? (True/False)
            2. What's the status message?
        """
        try:
            # Ask AWS about this load balancer's settings
            response = client.describe_load_balancer_attributes(
                LoadBalancerName=lb_name
            )
            
            # Get the logging settings (like checking camera settings)
            attributes = response['LoadBalancerAttributes']
            access_logs = attributes.get('AccessLog', {})
            
            # Check if logging is turned on
            is_enabled = access_logs.get('Enabled', False)
            
            if is_enabled:
                return True, "✅ Logging is enabled"
            return False, "❌ Logging is disabled"

        except ClientError as e:
            # Handle AWS-specific errors with clear messages
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"🚫 Error checking load balancer '{lb_name}': {error_message}")
            return False, f"Error: {error_code}"
        except Exception as e:
            # Handle any unexpected errors
            logger.error(f"❌ Unexpected error checking load balancer '{lb_name}': {str(e)}")
            return False, "Error: Unable to check logging configuration"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main method that checks all load balancers in the account.
        
        Think of this like doing a complete security audit of all cameras in a building:
        1. Get a list of all cameras (load balancers)
        2. Check each one to see if it's recording (logging)
        3. Create a report of what we found
        
        Returns: 
            A report card showing which load balancers passed or failed the check
        """
        # Initialize our report card
        report = CheckReport(name=__name__)
        report.passed = True  # Start optimistic - assume everything is good
        report.resource_ids_status = {}  # Will store results for each load balancer
        found_load_balancers = False  # Track if we found any load balancers

        try:
            # Connect to AWS ELB service
            elb_client = connection.client('elb')
            
            try:
                # Get list of all load balancers (like getting a list of all security cameras)
                paginator = elb_client.get_paginator('describe_load_balancers')
                
                for page in paginator.paginate():
                    if page['LoadBalancerDescriptions']:
                        found_load_balancers = True
                    
                    # Check each load balancer one by one
                    for lb in page['LoadBalancerDescriptions']:
                        lb_name = lb['LoadBalancerName']
                        
                        # Check if this load balancer has logging enabled
                        is_compliant, status_message = self.check_logging_enabled(
                            elb_client, lb_name
                        )
                        
                        # Record the results
                        resource_key = f"ELB:{lb_name}"
                        report.resource_ids_status[resource_key] = is_compliant
                        
                        # If any load balancer fails, the whole check fails
                        if not is_compliant:
                            report.passed = False
                            logger.info(f"⚠️ Load balancer '{lb_name}': {status_message}")

                # Handle the case where no load balancers were found
                if not found_load_balancers:
                    report.passed = False
                    report.resource_ids_status["No Load Balancers Found"] = False
                    logger.warning("ℹ️ No load balancers found to check")

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
