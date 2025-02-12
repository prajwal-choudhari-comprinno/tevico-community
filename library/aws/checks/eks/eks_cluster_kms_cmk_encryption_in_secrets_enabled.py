"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-10
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class eks_cluster_kms_cmk_encryption_in_secrets_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            client = connection.client('eks')
            paginator = client.get_paginator('list_clusters')
            account_id = connection.client('sts').get_caller_identity()['Account']
            region = client.meta.region_name

            # Paginate through all EKS clusters
            for page in paginator.paginate():
                clusters = page['clusters']
                for cluster_name in clusters:
                    cluster_desc = client.describe_cluster(name=cluster_name)['cluster']
                    cluster_arn = cluster_desc.get('arn', f"arn:aws:eks:{region}:{account_id}:cluster/{cluster_name}")
                    resource = AwsResource(arn=cluster_arn)
                    try:
                        encryption_configs = cluster_desc.get('encryptionConfig', [])
                        secrets_encrypted = any(
                            'provider' in config and config['provider'].get('keyArn') and 'secrets' in config.get('resources', [])
                            for config in encryption_configs
                        )
                        
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED if secrets_encrypted else CheckStatus.FAILED,
                                summary=f"Secrets encryption with KMS CMK {'enabled' if secrets_encrypted else 'not enabled'} for cluster {cluster_name}."
                            )
                        )
                        if not secrets_encrypted:
                            report.status = CheckStatus.FAILED
                    
                    except Exception as e:
                        report.status = CheckStatus.FAILED
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Error checking encryption for cluster {cluster_name}: {str(e)}"
                            )
                        )

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing EKS clusters: {str(e)}"
                )
            )

        return report
