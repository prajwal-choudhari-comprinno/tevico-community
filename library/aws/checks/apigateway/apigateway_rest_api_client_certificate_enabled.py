"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-13
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class apigateway_rest_api_client_certificate_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('apigateway')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            paginator = client.get_paginator('get_rest_apis')
            for page in paginator.paginate():
                for api in page.get('items', []):
                    api_id = api['id']
                    api_name = api.get('name', 'Unnamed API')
                    api_arn = f"arn:aws:apigateway::{api_id}"
                    resource = AwsResource(arn=api_arn)

                    try:
                        stages_response = client.get_stages(restApiId=api_id)
                        for stage in stages_response.get('item', []):
                            stage_name = stage.get('stageName', 'unknown')
                            has_cert = stage.get('clientCertificateId') is not None
                            
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=resource,
                                    status=CheckStatus.PASSED if has_cert else CheckStatus.FAILED,
                                    summary=f"Client certificate {'enabled' if has_cert else 'not enabled'} for {api_name}-{stage_name}."
                                )
                            )
                            
                            if not has_cert:
                                report.status = CheckStatus.FAILED
                    
                    except Exception as e:
                        report.status = CheckStatus.FAILED
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Error checking client certificate for {api_name}: {str(e)}"
                            )
                        )
        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing API Gateway: {str(e)}"
                )
            )

        return report
