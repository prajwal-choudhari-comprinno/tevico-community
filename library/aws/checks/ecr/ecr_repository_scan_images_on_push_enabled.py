"""
AUTHOR: RONIT CHAUHAN
EMAIL: ronit.chauhan@comprinno.net
DATE: 2024-11-07

This check evaluates whether Amazon ECR repositories have scan-on-push enabled.
The check will:
- PASS: If repository has scan-on-push enabled
- FAIL: If repository has scan-on-push disabled
- FAIL: If no ECR repositories exist
"""
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class ecr_repository_scan_images_on_push_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Execute the ECR repository scan-on-push check.
        
        Args:
            connection: boto3.Session object for AWS authentication
            
        Returns:
            CheckReport: Report containing check results
        """
        report = CheckReport(name=__name__)
        report.passed = True
        
        try:
            # Initialize ECR client
            client = connection.client('ecr')
            paginator = client.get_paginator('describe_repositories')
            
            # Track if we found any repositories
            repositories_found = False
            
            # List and check all ECR repositories
            for page in paginator.paginate():
                repositories = page.get('repositories', [])
                
                if repositories:
                    repositories_found = True
                    
                    for repo in repositories:
                        repo_name = repo['repositoryName']
                        scan_config = repo.get('imageScanningConfiguration', {})
                        scan_on_push = scan_config.get('scanOnPush', False)
                        
                        if scan_on_push:
                            # Repository has scan-on-push enabled
                            status_message = f"{repo_name}: ECR repository has scan on push enabled."
                            report.resource_ids_status[status_message] = True
                        else:
                            # Repository does not have scan-on-push enabled
                            status_message = f"{repo_name}: ECR repository does not have scan on push enabled."
                            report.resource_ids_status[status_message] = False
                            report.passed = False
            
            # Handle case where no repositories exist
            if not repositories_found:
                report.passed = False
                report.resource_ids_status["No ECR Repository Found"] = False
                
        except ClientError as ce:
            # Handle AWS API specific errors
            error_code = ce.response.get('Error', {}).get('Code', 'Unknown')
            error_message = ce.response.get('Error', {}).get('Message', 'Unknown error occurred')
            report.passed = False
            report.resource_ids_status[f"AWS Error ({error_code})"] = False
            
        except BotoCoreError as be:
            # Handle AWS SDK specific errors
            report.passed = False
            report.resource_ids_status["AWS SDK Error"] = False
            
        except Exception as e:
            # Handle any unexpected errors
            report.passed = False
            report.resource_ids_status["Unexpected Error"] = False
            
        return report
