"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-13
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class apigatewayv2_api_access_logging_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize API Gateway V2 client
            client = connection.client('apigatewayv2')
            
            # List all API Gateway V2 APIs
            apis = client.get_apis().get('Items', [])

            for api in apis:
                api_id = api['ApiId']
                api_name = api.get('Name', 'Unnamed API')
                region = connection.region_name

                # Construct the ARN format for API Gateway V2 APIs
                resource = AwsResource(
                    arn=f"arn:aws:apigateway:{region}::/apis/{api_id}"
                )

                try:
                    # List all stages for the current API
                    stages = client.get_stages(ApiId=api_id).get('Items', [])
                    api_has_logging = False

                    for stage in stages:
                        stage_name = stage.get('StageName', 'Unknown Stage')
                        access_logging_enabled = bool(stage.get('AccessLogSettings', {}).get('DestinationArn'))

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED if access_logging_enabled else CheckStatus.FAILED,
                                summary=f"Access logging {'enabled' if access_logging_enabled else 'not enabled'} for API {api_name} - Stage {stage_name}."
                            )
                        )

                        if access_logging_enabled:
                            api_has_logging = True

                    # If no stages have logging enabled, mark API as failed
                    if not api_has_logging:
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
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing API Gateway V2: {str(e)}"
                )
            )

        return report
