"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-12-30

Description: This script checks if Amazon ECR repositories have automatic image scanning enabled.
Think of it like a security checkpoint at an airport - we want to make sure all containers 
(like luggage) are automatically scanned for security issues when they arrive.

Why this matters:
- Container images might have security vulnerabilities
- Automatic scanning helps detect these issues early
- It's like having an X-ray machine that checks every piece of luggage automatically
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

class ecr_repository_scan_images_on_push_enabled(Check):
    """
    Security check for ECR repositories to ensure automatic scanning is enabled.
    Like making sure every airport has working X-ray machines for luggage inspection.
    """

    def check_repository_scanning(self, client, repository_name: str) -> tuple:
        """
        Checks if a specific repository has scan-on-push enabled.

        Think of this like checking if a specific security scanner is working:
        - If scanner is on (scanning enabled) = Good ✅
        - If scanner is off (scanning disabled) = Bad ❌

        Args:
            client: Our connection to AWS ECR (like security clearance)
            repository_name: Name of the repository to check

        Returns:
            Two pieces of information:
            1. Is scanning enabled? (True/False)
            2. Status message explaining the result
        """
        try:
            # Get repository settings
            response = client.describe_repositories(repositoryNames=[repository_name])
            repo_info = response['repositories'][0]
            
            # Check if scan on push is enabled
            scanning_config = repo_info.get('imageScanningConfiguration', {})
            is_scan_on_push = scanning_config.get('scanOnPush', False)
            
            if is_scan_on_push:
                return True, "✅ Scan on push is enabled"
            return False, "❌ Scan on push is disabled"

        except ClientError as e:
            # Handle AWS-specific errors
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"⚠️ Error checking repository '{repository_name}': {error_message}")
            return False, f"Error: {error_code}"
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"❌ Unexpected error checking repository '{repository_name}': {str(e)}")
            return False, "Error: Unable to check scanning configuration"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main method to check all ECR repositories.

        Think of this like doing a security audit of all airport scanners:
        1. Find all security checkpoints (repositories)
        2. Check if each checkpoint has automatic scanning
        3. Create a report of what we found

        Returns:
            A report card showing which repositories are secure
        """
        # Initialize our report card
        report = CheckReport(name=__name__)
        report.passed = True  # Start optimistic - assume everything is good
        report.resource_ids_status = {}  # Will store results for each repository
        found_repositories = False

        try:
            # Connect to AWS ECR service
            ecr_client = connection.client('ecr')
            
            try:
                # Get list of all repositories
                paginator = ecr_client.get_paginator('describe_repositories')
                
                for page in paginator.paginate():
                    if page['repositories']:
                        found_repositories = True
                        
                        # Check each repository
                        for repo in page['repositories']:
                            repo_name = repo['repositoryName']
                            
                            # Check if scanning is enabled
                            is_compliant, status_message = self.check_repository_scanning(
                                ecr_client, repo_name
                            )
                            
                            # Record the results
                            resource_key = f"ECR:{repo_name}"
                            report.resource_ids_status[resource_key] = is_compliant
                            
                            if not is_compliant:
                                report.passed = False
                                logger.warning(f"🚨 Repository '{repo_name}': {status_message}")
                            else:
                                logger.info(f"✅ Repository '{repo_name}' has scanning enabled")

                # Handle case where no repositories were found
                if not found_repositories:
                    report.passed = False
                    report.resource_ids_status["No ECR Repositories Found"] = False
                    logger.warning("ℹ️ No ECR repositories found to check")

            except ClientError as e:
                # Handle AWS API errors
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDenied':
                    logger.error("🔒 Access denied - check your permissions")
                else:
                    logger.error(f"⚠️ Error listing repositories: {e.response['Error']['Message']}")
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
