"""
AUTHOR: RONIT CHAUHAN
EMAIL: ronit.chauhan@comprinno.net
DATE: 2024-11-07

Description: This script checks for vulnerabilities in the latest images of ECR repositories.
It's like a security inspection system that:
1. Finds the newest container image in each repository
2. Checks if it has been scanned for security issues
3. Reviews the severity of any found vulnerabilities
4. Reports if the security level meets our standards
"""
"""
ECR Repository Vulnerability Scanner Check

This check evaluates the security vulnerabilities in the latest images of ECR repositories.
It performs the following:
1. Identifies the latest image in each ECR repository
2. Verifies if security scanning has been completed
3. Evaluates vulnerability findings against defined severity thresholds
4. Reports compliance status based on vulnerability severity

PASS Conditions:
- Repository exists with images
- Latest image has been scanned
- No vulnerabilities at or above the defined severity threshold

FAIL Conditions:
- No repositories found
- Repository exists but has no images
- Scan not completed or not found
- Vulnerabilities found at or above severity threshold
- Access or permission issues
"""
import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

class ecr_repository_scan_vulnerabilities_in_latest_image(Check):
    def __init__(self, metadata=None):
        """
        Initialize check with configuration parameters.
        
        Args:
            metadata: Additional metadata for the check
        """
        super().__init__(metadata)
        self.severity_threshold = "MEDIUM"
        self.severity_levels = {
            "CRITICAL": 3,
            "HIGH": 2,
            "MEDIUM": 1,
            "LOW": 0
        }

    def evaluate_vulnerabilities(self, findings: dict) -> tuple:
        """
        Evaluate scan findings and count vulnerabilities by severity level.
        
        Args:
            findings: Dictionary containing vulnerability scan results
            
        Returns:
            tuple: (is_compliant: bool, message: str)
        """
        if not findings:
            return True, self.format_vulnerability_message({})

        severity_counts = findings.get('findingSeverityCounts', {})
        threshold_level = self.severity_levels[self.severity_threshold]
        
        # Initialize counts for all severity levels
        vulnerability_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
        
        # Update counts from findings
        for severity, count in severity_counts.items():
            if severity.upper() in vulnerability_counts:
                vulnerability_counts[severity.upper()] = count

        # Check if any vulnerabilities above threshold exist
        has_critical_vulnerabilities = any(
            self.severity_levels.get(severity, 0) >= threshold_level and count > 0
            for severity, count in severity_counts.items()
        )

        return (False if has_critical_vulnerabilities else True,
                self.format_vulnerability_message(vulnerability_counts))

    def format_vulnerability_message(self, counts: dict) -> str:
        """
        Format vulnerability counts into a standardized message.
        
        Args:
            counts: Dictionary of vulnerability counts by severity
            
        Returns:
            str: Formatted message with vulnerability counts
        """
        default_counts = {
            "CRITICAL": counts.get("CRITICAL", 0),
            "HIGH": counts.get("HIGH", 0),
            "MEDIUM": counts.get("MEDIUM", 0),
            "LOW": counts.get("LOW", 0)
        }
        
        if sum(default_counts.values()) > 0:
            return (f"vulnerabilities detected: Critical = {default_counts['CRITICAL']}, "
                   f"High = {default_counts['HIGH']}, Medium = {default_counts['MEDIUM']}, "
                   f"Low = {default_counts['LOW']}")
        else:
            return (f"No critical vulnerabilities found: Critical = 0, "
                   f"High = 0, Medium = 0, Low = 0")

    def process_repository(self, client, repo_name: str) -> tuple:
        """
        Process individual repository for vulnerability scanning.
        
        Args:
            client: ECR client
            repo_name: Name of the repository
            
        Returns:
            tuple: (is_compliant: bool, status_message: str)
        """
        try:
            # Get images in repository
            images_response = client.list_images(
                repositoryName=repo_name,
                filter={'tagStatus': 'TAGGED'}
            )

            if not images_response.get('imageIds'):
                return False, f"{repo_name}: No images found"

            # Get latest image details
            image_details = client.describe_images(
                repositoryName=repo_name,
                imageIds=images_response['imageIds']
            ).get('imageDetails', [])

            if not image_details:
                return False, f"{repo_name}: No image details found"

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

                scan_status = scan_result.get('imageScanStatus', {}).get('status')
                if scan_status != 'COMPLETE':
                    return False, f"{repo_name}: Scan status - {scan_status}"

                is_compliant, message = self.evaluate_vulnerabilities(
                    scan_result.get('imageScanFindings', {})
                )
                
                return is_compliant, f"{repo_name}: {message}"

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ScanNotFoundException':
                    # Explicitly handle the case where scan is not found
                    return False, f"{repo_name}: Scan not found"
                raise  # Re-raise other ClientErrors to be handled by outer try-except

        except ClientError as e:
            error_code = e.response['Error']['Code']
            return False, f"{repo_name}: {error_code}"

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Execute vulnerability scan check across all repositories.
        
        Args:
            connection: AWS session
            
        Returns:
            CheckReport: Results of the vulnerability scan check
        """
        report = CheckReport(name=__name__)
        report.passed = True

        try:
            client = connection.client('ecr')
            paginator = client.get_paginator('describe_repositories')
            
            repositories_found = False
            for page in paginator.paginate():
                if page.get('repositories'):
                    repositories_found = True
                    for repo in page['repositories']:
                        is_compliant, status_message = self.process_repository(
                            client, 
                            repo['repositoryName']
                        )
                        report.resource_ids_status[status_message] = is_compliant
                        if not is_compliant:
                            report.passed = False

            if not repositories_found:
                report.passed = False
                report.resource_ids_status["No ECR Repositories Found"] = False

        except ClientError as e:
            report.passed = False
            error_code = e.response['Error']['Code']
            report.resource_ids_status[f"AWS Error: {error_code}"] = False

        except NoCredentialsError:
            report.passed = False
            report.resource_ids_status["AWS Credentials Not Found"] = False

        except EndpointConnectionError:
            report.passed = False
            report.resource_ids_status["AWS Connection Error"] = False

        except Exception as e:
            report.passed = False
            report.resource_ids_status[f"Unexpected Error: {str(e)}"] = False

        return report
