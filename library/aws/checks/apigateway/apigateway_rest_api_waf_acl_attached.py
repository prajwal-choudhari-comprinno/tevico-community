"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-13
"""

import boto3
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class apigateway_rest_api_waf_acl_attached(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []
        
        try:
            apigw_client = connection.client('apigateway')
            wafv2_client = connection.client('wafv2')
            region = connection.client('sts').get_caller_identity().get('Arn').split(':')[3]
            
            paginator = apigw_client.get_paginator('get_rest_apis')
            for page in paginator.paginate():
                for api in page.get('items', []):
                    api_id = api['id']
                    api_name = api.get('name', 'Unnamed API')
                    api_arn = f"arn:aws:apigateway:{region}::/restapis/{api_id}"
                    resource = AwsResource(arn=api_arn)
                    
                    try:
                        stages_response = apigw_client.get_stages(restApiId=api_id)
                        api_has_waf = False
                        
                        for stage in stages_response.get('item', []):
                            stage_name = stage['stageName']
                            stage_arn = f"{api_arn}/stages/{stage_name}"
                            
                            try:
                                wafv2_response = wafv2_client.get_web_acl_for_resource(ResourceArn=stage_arn)
                                if wafv2_response.get('WebACL'):
                                    api_has_waf = True
                                    break
                            except wafv2_client.exceptions.WAFNonexistentItemException:
                                continue
                            except wafv2_client.exceptions.WAFInvalidParameterException:
                                continue
                            except Exception as e:
                                report.resource_ids_status.append(
                                    ResourceStatus(
                                        resource=resource,
                                        status=CheckStatus.FAILED,
                                        summary=f"Error checking WAF for stage {stage_name}: {str(e)}"
                                    )
                                )
                                report.status = CheckStatus.FAILED
                                
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED if api_has_waf else CheckStatus.FAILED,
                                summary=f"WAF ACL {'attached' if api_has_waf else 'not attached'} to API {api_name}."
                            )
                        )
                        if not api_has_waf:
                            report.status = CheckStatus.FAILED
                    except Exception as e:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Error retrieving stages for API {api_name}: {str(e)}"
                            )
                        )
                        report.status = CheckStatus.FAILED
                        
        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(resource=""),
                    status=CheckStatus.FAILED,
                    summary=f"Error accessing API Gateway REST APIs: {str(e)}"
                )
            )
        
        return report
