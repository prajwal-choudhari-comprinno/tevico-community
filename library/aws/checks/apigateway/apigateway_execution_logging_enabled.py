"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-13
"""

import re
import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class apigateway_execution_logging_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            client = connection.client('apigateway')
            apis = client.get_rest_apis().get('items', [])
            
            for api in apis:
                api_id = api['id']
                api_name = api.get('name', 'Unnamed API')
                region = connection.region_name

                # Construct the correct ARN format for REST API
                resource = AwsResource(
                    arn=f"arn:aws:apigateway:{region}::/restapis/{api_id}"
                )
                
                try:
                    stages = client.get_stages(restApiId=api_id).get('item', [])
                    for stage in stages:
                        stage_name = stage.get('stageName', 'Unknown Stage')
                        logging_enabled = any(
                            settings.get('loggingLevel') in ['ERROR', 'INFO']
                            for settings in stage.get('methodSettings', {}).values()
                        )
                        
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED if logging_enabled else CheckStatus.FAILED,
                                summary=f"Execution logging {'enabled' if logging_enabled else 'not enabled'} for API {api_name} - Stage {stage_name}."
                            )
                        )
                        
                        if not logging_enabled:
                            report.status = CheckStatus.FAILED
                
                except Exception as e:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.FAILED,
                            summary=f"Error retrieving stages for API {api_name}: {str(e)}"
                        )
                    )
        
        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing API Gateway: {str(e)}"
                )
            )
       
        return report
