"""
AUTHOR: Supriyo Bhakat
EMAIL: supriyo.bhakat@comprinno.net
DATE: 2024-11-15
"""


import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class config_recorder_all_regions_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.FAILED
        report.resource_ids_status = []
        config_client = connection.client('config')

        response = config_client.describe_configuration_recorder_status()
        recorders = response.get('ConfigurationRecordersStatus', [])

        if not recorders:
            report.status = CheckStatus.FAILED
            return report

        all_regions_enabled = True
        for recorder in recorders:
            recorder_name = recorder['name']
            is_enabled = recorder.get('recording', False)

            if not is_enabled:
                all_regions_enabled = False
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=recorder_name),
                        status=CheckStatus.FAILED,
                        summary=''
                    )
                )
            else:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=recorder_name),
                        status=CheckStatus.PASSED,
                        summary=''
                    )
                )

        if all_regions_enabled:
            report.status = CheckStatus.PASSED

        return report
