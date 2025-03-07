"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-16
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus
from tevico.engine.entities.check.check import Check

class macie_status_check(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('macie2')
        report = CheckReport(name=__name__)

        try:
            macie_status = client.get_macie_session()
            if macie_status['status'] == 'ENABLED':
                report.status = CheckStatus.PASSED
            else:
                report.status = CheckStatus.FAILED
        except Exception as e:
            report.status = CheckStatus.FAILED

        return report
