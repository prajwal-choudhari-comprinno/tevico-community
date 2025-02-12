"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-07
"""
    
import boto3
from tevico.engine.entities.report.check_model import AwsResource, GeneralResource, CheckReport, CheckStatus, ResourceStatus
from tevico.engine.entities.check.check import Check

class ecr_image_private_image_scanning_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('ecr')
        paginator = client.get_paginator('describe_repositories')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # List all ECR repositories
            has_repositories = False
            for page in paginator.paginate():
                repositories = page.get('repositories', [])
                if repositories:
                    has_repositories = True
                
                for repo in repositories:
                    repo_name = repo['repositoryName']
                    repo_arn = repo.get('repositoryArn')
                    
                    # Skip public repositories
                    if repo.get('repositoryUri', '').startswith("public.ecr.aws"):
                        continue  
                    
                    scan_on_push = repo.get('imageScanningConfiguration', {}).get('scanOnPush', False)
                    
                    if scan_on_push:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=repo_arn),
                                status=CheckStatus.PASSED,
                                summary=f"ECR repository {repo_name} has image scanning on push enabled."
                            )
                        )
                    else:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=repo_arn),
                                status=CheckStatus.FAILED,
                                summary=f"ECR repository {repo_name} does not have image scanning on push enabled."
                            )
                        )
                        report.status = CheckStatus.FAILED
            
            if not has_repositories:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(resource=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No ECR repositories found."
                    )
                )
        
        except Exception as e:
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error fetching ECR repositories: {str(e)}"
                )
            )
            report.status = CheckStatus.FAILED
        return report
