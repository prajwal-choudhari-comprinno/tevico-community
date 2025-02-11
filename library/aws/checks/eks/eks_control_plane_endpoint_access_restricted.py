"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-10
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class eks_control_plane_endpoint_access_restricted(Check):

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
                        endpoint_config = cluster_desc.get('resourcesVpcConfig', {})
                        public_access_enabled = endpoint_config.get('endpointPublicAccess', True)

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED if public_access_enabled else CheckStatus.PASSED,
                                summary=f"Public endpoint access is {'enabled' if public_access_enabled else 'restricted'} for cluster {cluster_name}."
                            )
                        )
                        if public_access_enabled:
                            report.status = CheckStatus.FAILED
                    
                    except Exception as e:
                        report.status = CheckStatus.FAILED
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Error checking endpoint access for cluster {cluster_name}: {str(e)}"
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
