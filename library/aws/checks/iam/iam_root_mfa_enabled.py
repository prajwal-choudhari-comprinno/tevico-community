"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-14
"""

import boto3
import logging

from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class iam_root_mfa_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []
        
        try:
            client = connection.client("iam")

            # Fetch account summary
            account_summary = client.get_account_summary()
            
            root_mfa_enabled = account_summary.get("SummaryMap", {}).get("AccountMFAEnabled", 0) == 1

            # Update report based on MFA status
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.PASSED if root_mfa_enabled else CheckStatus.FAILED,
                    summary=f"Root account MFA is {'enabled' if root_mfa_enabled else 'not enabled'}."
                )
            )

        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.PASSED if root_mfa_enabled else CheckStatus.ERRORED,
                    summary=f"Error while checking root MFA configuration.",
                    exception=str(e)
                )
            )

        return report
