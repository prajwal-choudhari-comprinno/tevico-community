"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-16
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus
from tevico.engine.entities.check.check import Check
from botocore.exceptions import ClientError

class guardduty_is_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        
        try:
            available_regions = connection.get_available_regions('guardduty')

            for region in available_regions:
                try:
                    regional_client = connection.client('guardduty', region_name=region)
                    detectors = regional_client.list_detectors()

                    if not detectors.get('DetectorIds', []):
                        report.status = CheckStatus.FAILED
                        continue

                    for detector_id in detectors['DetectorIds']:
                        try:
                            detector = regional_client.get_detector(DetectorId=detector_id)
                            if detector.get('Status') is None or not detector.get('Status'):
                                report.status = CheckStatus.FAILED
                            else:
                                report.status = CheckStatus.PASSED
                        except ClientError:
                            report.status = CheckStatus.FAILED

                except ClientError:
                    report.status = CheckStatus.FAILED

        except Exception:
            report.status = CheckStatus.FAILED

        return report

