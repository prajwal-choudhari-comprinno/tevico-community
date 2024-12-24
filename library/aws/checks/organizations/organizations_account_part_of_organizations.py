"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-10-17
"""
"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-10-17

Description: This code checks if an AWS account is part of an AWS Organization.
Think of it like checking if a branch office is properly connected to its headquarters.
"""

import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
from datetime import datetime

# Set up logging to track what's happening
logger = logging.getLogger(__name__)

class organizations_account_part_of_organizations(Check):
    """
    This check verifies if the AWS account is part of an AWS Organization.
    Like checking if a branch office is properly registered with headquarters.
    """

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main function to check organization membership.
        Returns a detailed report of the findings.
        """
        # Start timing the check execution
        start_time = datetime.now()
        
        # Create a report object
        report = CheckReport(name=__name__)
        
        try:
            # Step 1: Connect to AWS Organizations service
            logger.info("Connecting to AWS Organizations service")
            try:
                org_client = connection.client('organizations')
                logger.info("Successfully connected to AWS Organizations")
            except (BotoCoreError, ClientError) as e:
                error_msg = f"Cannot connect to AWS Organizations: {str(e)}"
                logger.error(error_msg)
                raise ConnectionError(error_msg)

            # Step 2: Try to get organization details
            try:
                # Attempt to describe the organization
                org_details = org_client.describe_organization()
                organization = org_details.get('Organization', {})
                
                # Extract important organization information
                org_id = organization.get('Id', 'Unknown')
                org_arn = organization.get('Arn', 'Unknown')
                org_status = organization.get('Status', 'Unknown')
                
                logger.info(f"Found organization: {org_id} with status: {org_status}")

                # Step 3: Check organization status and prepare report
                if org_status == "ACTIVE":
                    report.passed = True
                    report.resource_ids_status = {org_id: True}
                    report.report_metadata = {
                        "status": "PASS",
                        "message": f"Account is part of active AWS Organization: {org_id}",
                        "details": {
                            "organization_id": org_id,
                            "organization_arn": org_arn,
                            "status": org_status,
                            "master_account": organization.get('MasterAccountId', 'Unknown'),
                            "feature_set": organization.get('FeatureSet', 'Unknown'),
                            "check_time": datetime.now().isoformat()
                        }
                    }
                    logger.info("Check passed - Account is part of active organization")
                else:
                    report.passed = False
                    report.resource_ids_status = {org_id: False}
                    report.report_metadata = {
                        "status": "FAIL",
                        "message": f"Organization exists but status is: {org_status}",
                        "details": {
                            "organization_id": org_id,
                            "organization_arn": org_arn,
                            "status": org_status,
                            "check_time": datetime.now().isoformat()
                        },
                        "recommendation": "Verify organization status and configuration"
                    }
                    logger.warning(f"Check failed - Organization status is {org_status}")

            except org_client.exceptions.AWSOrganizationsNotInUseException:
                # Handle case when Organizations is not being used
                report.passed = False
                report.resource_ids_status = {"no_organization": False}
                report.report_metadata = {
                    "status": "FAIL",
                    "message": "AWS Organizations is not in use for this account",
                    "recommendation": "Consider using AWS Organizations for better account management",
                    "check_time": datetime.now().isoformat()
                }
                logger.warning("AWS Organizations is not in use")

        except org_client.exceptions.AccessDeniedException as e:
            # Handle permission issues
            error_msg = "Access denied while checking organization details"
            logger.error(f"{error_msg}: {str(e)}")
            report.passed = False
            report.report_metadata = {
                "status": "ERROR",
                "error": error_msg,
                "exception": str(e),
                "recommendation": "Check IAM permissions for Organizations access",
                "check_time": datetime.now().isoformat()
            }

        except (BotoCoreError, ClientError) as e:
            # Handle AWS-specific errors
            error_msg = "Error while checking organization details"
            logger.error(f"{error_msg}: {str(e)}")
            report.passed = False
            report.report_metadata = {
                "status": "ERROR",
                "error": error_msg,
                "exception": str(e),
                "recommendation": "Check AWS service availability",
                "check_time": datetime.now().isoformat()
            }

        except Exception as e:
            # Handle unexpected errors
            error_msg = "Unexpected error during organization check"
            logger.error(f"{error_msg}: {str(e)}")
            report.passed = False
            report.report_metadata = {
                "status": "ERROR",
                "error": error_msg,
                "exception": str(e),
                "recommendation": "Check system logs for details",
                "check_time": datetime.now().isoformat()
            }

        finally:
            # Calculate and log execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Check completed in {execution_time} seconds")
            
            # Add execution time to metadata if it exists
            if hasattr(report, 'report_metadata') and isinstance(report.report_metadata, dict):
                report.report_metadata["execution_time"] = execution_time

        return report


    # Pass Condition: If the organization is ENABLED, it adds a "PASS" status confirming that the AWS Organization contains the AWS account.
    # Fail Condition: If the status is not "ENABLED", it adds a "FAIL" status that the AWS Organization is not in use.