"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-07
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, GeneralResource, CheckReport, CheckStatus, ResourceStatus
from tevico.engine.entities.check.check import Check

class ecr_repository_scan_vulnerabilities_in_latest_image(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('ecr')
        paginator = client.get_paginator('describe_repositories')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # List all ECR repositories
            repositories = []
            for page in paginator.paginate():
                repositories.extend(page.get('repositories', []))

            if not repositories:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(resource=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No ECR repositories found."
                    )
                )
                return report

            for repo in repositories:
                repo_name = repo['repositoryName']
                resource = AwsResource(arn=repo.get('repositoryArn', f"unknown-arn-for-{repo_name}"))
                try:
                    images = client.list_images(
                        repositoryName=repo_name,
                        filter={'tagStatus': 'TAGGED'}
                    ).get('imageIds', [])

                    if not images:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.NOT_APPLICABLE,
                                summary=f"No images found in repository {repo_name}."
                            )
                        )
                        continue

                    image_details = client.describe_images(
                        repositoryName=repo_name,
                        imageIds=images
                    ).get('imageDetails', [])

                    if not image_details:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.NOT_APPLICABLE,
                                summary=f"No image details available for repository {repo_name}."
                            )
                        )
                        continue

                    latest_image = sorted(image_details, key=lambda x: x['imagePushedAt'], reverse=True)[0]

                    scan_result = client.describe_image_scan_findings(
                        repositoryName=repo_name,
                        imageId={'imageDigest': latest_image['imageDigest']}
                    )

                    findings_summary = scan_result.get('imageScanFindingsSummary', {})
                    vulnerabilities_found = findings_summary.get('findingSeverityCounts', {})

                    if vulnerabilities_found:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Vulnerabilities found in latest image of repository {repo_name}."
                            )
                        )
                        report.status = CheckStatus.FAILED
                    else:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED,
                                summary=f"No vulnerabilities found in latest image of repository {repo_name}."
                            )
                        )

                except client.exceptions.RepositoryNotFoundException:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=f"ECR repository {repo_name} not found."
                        )
                    )
                    report.status = CheckStatus.FAILED
                except client.exceptions.ImageNotFoundException:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.NOT_APPLICABLE,
                            summary=f"No scanned image found in repository {repo_name}."
                        )
                    )
                except Exception as e:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=f"Error checking scan results for repository {repo_name}: {str(e)}",
                            exception=e
                        )
                    )
                    report.status = CheckStatus.FAILED

        except Exception as e:
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error listing ECR repositories: {str(e)}"
                )
            )
            report.status = CheckStatus.FAILED

        return report
