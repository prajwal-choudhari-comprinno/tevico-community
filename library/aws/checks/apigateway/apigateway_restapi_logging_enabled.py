import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class apigateway_restapi_logging_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            client = connection.client('apigateway')
            apis = client.get_rest_apis().get('items', [])
            region = connection.client('sts').get_caller_identity().get('Arn').split(':')[3]

            for api in apis:
                api_name = api.get('name', 'Unnamed API')
                api_id = api['id']
                api_arn = f"arn:aws:apigateway:{region}::/restapis/{api_id}"
                resource = AwsResource(arn=api_arn)

                try:
                    logging_types = api.get('endpointConfiguration', {}).get('types', [])
                    logging_enabled = 'REGIONAL' in logging_types

                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.PASSED if logging_enabled else CheckStatus.FAILED,
                            summary=f"Logging {'enabled' if logging_enabled else 'not enabled'} for API {api_name}."
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
                            summary=f"Error checking logging for API {api_name}: {str(e)}"
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
