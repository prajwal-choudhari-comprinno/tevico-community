"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-03-21
"""


import boto3
from botocore.exceptions import BotoCoreError, ClientError

from tevico.engine.entities.report.check_model import (
    CheckReport, CheckStatus, AwsResource, GeneralResource, ResourceStatus
)
from tevico.engine.entities.check.check import Check


class config_recorder_all_regions_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.resource_ids_status = []

        try:
            ec2_client = connection.client('ec2')
            paginator = ec2_client.get_paginator('describe_regions')
            all_regions = []
            
            for page in paginator.paginate():
                all_regions.extend(region['RegionName'] for region in page['Regions'])
            
            enabled_regions = []
            missing_regions = []

            for region in all_regions:
                try:
                    regional_client = connection.client('config', region_name=region)
                    paginator = regional_client.get_paginator('describe_configuration_recorders')
                    recorders = []
                    
                    for page in paginator.paginate():
                        recorders.extend(page.get('ConfigurationRecorders', []))
                    
                    if recorders:
                        enabled_regions.append(region)
                    else:
                        missing_regions.append(region)
                except (BotoCoreError, ClientError) as e:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=region),
                            status=CheckStatus.UNKNOWN,
                            summary=f"Error checking AWS Config recorder in region {region}.",
                            exception=str(e)
                        )
                    )

            if missing_regions:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name="AWS Config"),
                        status=CheckStatus.FAILED,
                        summary=f"AWS Config recorder is not enabled in the following regions: {', '.join(missing_regions)}."
                    )
                )

            if enabled_regions:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name="AWS Config"),
                        status=CheckStatus.PASSED,
                        summary=f"AWS Config recorder is enabled in the following regions: {', '.join(enabled_regions)}."
                    )
                )

        except Exception as e:
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="AWS Config"),
                    status=CheckStatus.UNKNOWN,
                    summary="Encountered an error while retrieving AWS Config recorder status.",
                    exception=str(e)
                )
            )

        return report
