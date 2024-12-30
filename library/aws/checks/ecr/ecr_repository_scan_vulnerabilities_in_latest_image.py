"""
AUTHOR: RONIT CHAUHAN
DATE: [Current Date]

Description: This script checks for vulnerabilities in the latest images of ECR repositories.
It's like a security inspection system that:
1. Finds the newest container image in each repository
2. Checks if it has been scanned for security issues
3. Reviews the severity of any found vulnerabilities
4. Reports if the security level meets our standards
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
import logging
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ecr_repository_scan_vulnerabilities_in_latest_image(Check):
    """
    Checks ECR repositories for vulnerabilities in their latest images.
    """
    
    def __init__(self, metadata=None):
        """Initialize with metadata and set severity threshold"""
        super().__init__(metadata)
        # Configure minimum severity level for failing the check
        self.severity_threshold = "MEDIUM"  # Options: "CRITICAL", "HIGH", "MEDIUM"
        self.severity_levels = {
            "CRITICAL": 3,
            "HIGH": 2,
            "MEDIUM": 1,
            "LOW": 0
        }

    def evaluate_vulnerabilities(self, findings: dict) -> tuple:
        """
        Evaluates scan findings against severity threshold.
        
        Args:
            findings: Scan findings from ECR
            
        Returns:
            Tuple of (is_compliant, message)
        """
        if not findings:
            return True, "No vulnerabilities found"

        severity_counts = findings.get('findingSeverityCounts', {})
        threshold_level = self.severity_levels[self.severity_threshold]
        
        # Check each severity level against threshold
        for severity, count in severity_counts.items():
            if (self.severity_levels.get(severity, 0) >= threshold_level and count > 0):
                return False, f"Found {count} {severity} vulnerabilities"
                
        return True, "No critical vulnerabilities found"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main execution method that checks all repositories.
        
        Args:
            connection: AWS session
            
        Returns:
            CheckReport with findings
        """
        report = CheckReport(name=__name__)
        report.passed = True
        report.resource_ids_status = {}
        found_repositories = False
        repositories_without_images = []

        try:
            # Initialize ECR client
            client = connection.client('ecr')
            paginator = client.get_paginator('describe_repositories')

            # Iterate through all repositories
            try:
                repositories_list = []
                for page in paginator.paginate():
                    if page.get('repositories'):
                        found_repositories = True
                        repositories_list.extend(page['repositories'])

                if not found_repositories:
                    # No ECR repositories found
                    report.passed = False
                    report.resource_ids_status["No ECR Repositories Found"] = False
                    logger.warning("ℹ️ No ECR repositories found")
                    return report

                # Process repositories
                for repo in repositories_list:
                    repo_name = repo['repositoryName']

                    try:
                        # Get images in repository
                        images_response = client.list_images(
                            repositoryName=repo_name,
                            filter={'tagStatus': 'TAGGED'}
                        )

                        if not images_response.get('imageIds'):
                            repositories_without_images.append(repo_name)
                            continue

                        # Get image details
                        image_details = client.describe_images(
                            repositoryName=repo_name,
                            imageIds=images_response['imageIds']
                        ).get('imageDetails', [])

                        if not image_details:
                            repositories_without_images.append(repo_name)
                            continue

                        # Get latest image
                        latest_image = sorted(
                            image_details,
                            key=lambda x: x.get('imagePushedAt', 0),
                            reverse=True
                        )[0]

                        try:
                            # Get scan findings
                            scan_result = client.describe_image_scan_findings(
                                repositoryName=repo_name,
                                imageId={'imageDigest': latest_image['imageDigest']}
                            )

                            # Check scan status
                            scan_status = scan_result.get('imageScanStatus', {}).get('status')
                            if scan_status != 'COMPLETE':
                                report.resource_ids_status[f"ECR:{repo_name} : Scan Status - {scan_status}"] = False
                                logger.warning(f"🔍 Scan not complete for {repo_name}: {scan_status}")
                                report.passed = False
                                continue

                            # Evaluate findings
                            is_compliant, message = self.evaluate_vulnerabilities(
                                scan_result.get('imageScanFindings', {})
                            )
                            
                            if not is_compliant:
                                report.resource_ids_status[f"ECR:{repo_name} : {message}"] = False
                                report.passed = False
                                logger.warning(f"🚨 {repo_name}: {message}")
                            else:
                                report.resource_ids_status[f"ECR:{repo_name}"] = True
                                logger.info(f"✅ {repo_name}: {message}")

                        except ClientError as e:
                            if e.response['Error']['Code'] == 'ScanNotFoundException':
                                report.resource_ids_status[f"ECR:{repo_name} : No Scan Found"] = False
                                logger.error(f"❌ No scan found for {repo_name}")
                                report.passed = False
                            else:
                                raise e

                    except ClientError as e:
                        report.resource_ids_status[f"ECR:{repo_name} : Error - {e.response['Error']['Code']}"] = False
                        logger.error(f"⚠️ Error processing repository {repo_name}: {e.response['Error']['Message']}")
                        report.passed = False

                # Handle repositories without images
                if repositories_without_images:
                    if len(repositories_without_images) == len(repositories_list):
                        # All repositories are empty
                        report.resource_ids_status = {"No Images Found In Any ECR Repository": False}
                    else:
                        # Some repositories are empty
                        for repo_name in repositories_without_images:
                            report.resource_ids_status[f"ECR:{repo_name} : No Images Found"] = False
                    report.passed = False

            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logger.error("🔒 Access denied - check your permissions")
                    report.resource_ids_status["Access Denied"] = False
                else:
                    logger.error(f"⚠️ Error listing repositories: {e.response['Error']['Message']}")
                    report.resource_ids_status["Error"] = False
                report.passed = False

        except NoCredentialsError:
            logger.error("🔑 AWS credentials not found")
            report.passed = False
            report.resource_ids_status["No AWS Credentials"] = False

        except EndpointConnectionError:
            logger.error("🌐 Cannot connect to AWS")
            report.passed = False
            report.resource_ids_status["Connection Error"] = False

        except Exception as e:
            logger.error(f"💥 Unexpected error: {str(e)}")
            report.passed = False
            report.resource_ids_status["Error"] = False

        return report
