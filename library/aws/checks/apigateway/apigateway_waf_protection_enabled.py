"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-13
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class apigateway_waf_protection_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize clients
            client = connection.client('apigateway')
            waf_client = connection.client('wafv2')

            # Retrieve all REST APIs
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
                    # Get the stages for this API
                    stages = client.get_stages(restApiId=api_id).get('item', [])
                    api_protected = False

                    for stage in stages:
                        stage_name = stage.get('stageName', 'Unknown Stage')
                        stage_arn = f"arn:aws:apigateway:{region}::/restapis/{api_id}/stages/{stage_name}"

                        try:
                            # Check if WAF ACL is attached
                            web_acl = waf_client.get_web_acl_for_resource(ResourceArn=stage_arn)

                            if web_acl.get('WebACL'):
                                api_protected = True
                                break  # If WAF is found, no need to check further stages

                        except waf_client.exceptions.WAFNonexistentItemException:
                            continue
                        except waf_client.exceptions.WAFInvalidParameterException:
                            continue
                        except Exception as e:
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=resource,
                                    status=CheckStatus.FAILED,
                                    summary=f"Error checking WAF for API {api_name} - Stage {stage_name}: {str(e)}"
                                )
                            )

                    # Append the final result for this API
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.PASSED if api_protected else CheckStatus.FAILED,
                            summary=f"WAF protection {'enabled' if api_protected else 'not enabled'} for API {api_name}."
                        )
                    )

                    if not api_protected:
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
