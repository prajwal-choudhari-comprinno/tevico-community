"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-07
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class ecr_repository_scan_vulnerabilities_in_latest_image(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('ecr')
        paginator = client.get_paginator('describe_repositories')
        report = CheckReport(name=__name__)
        report.passed = True
        # List all ECR repositories
        for page in paginator.paginate():
            repositories = page['repositories']
            for repo in repositories:
                repo_name = repo['repositoryName']
                # Get the latest image details for the repository
                images = client.list_images(
                    repositoryName=repo_name,
                    filter={'tagStatus': 'TAGGED'}
                )['imageIds']
                
                if not images:
                    # No images to scan
                    report.resource_ids_status[repo_name] = True
                    continue
                # Get the latest image by the most recent push
                latest_image = sorted(images, key=lambda x: x['imagePushedAt'], reverse=True)[0]
                # Check scan findings for the latest image
                scan_result = client.describe_image_scan_findings(
                    repositoryName=repo_name,
                    imageId=latest_image
                )
                # Determine if vulnerabilities are found
                findings_summary = scan_result['imageScanFindingsSummary']
                vulnerabilities_found = findings_summary.get('findingSeverityCounts', {})

                if vulnerabilities_found:
                    # If any vulnerabilities are found, fail the check
                    report.resource_ids_status[repo_name] = False
                    report.passed = False
                else:
                    # No vulnerabilities found
                    report.resource_ids_status[repo_name] = True

        return report
