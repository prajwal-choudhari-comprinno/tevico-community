"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-14
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import (
    CheckReport, CheckStatus, GeneralResource, ResourceStatus
)
from tevico.engine.entities.check.check import Check


class iam_no_root_access_keys(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client("iam")
        report = CheckReport(name=__name__)
        report.resource_ids_status = []

        try:
            # Get Account Summary to check if root has access keys
            summary = client.get_account_summary()
            print(summary)
            root_access_keys = summary.get("SummaryMap", {}).get("AccountAccessKeysPresent", 0)

            if root_access_keys > 0:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name="Root Account"),
                        status=CheckStatus.FAILED,
                        summary="Root account has active access keys. It is recommended to remove them immediately."
                    )
                )
            else:
                report.status = CheckStatus.PASSED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name="Root Account"),
                        status=CheckStatus.PASSED,
                        summary="Root account has no active access keys."
                    )
                )

        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="Root Account"),
                    status=CheckStatus.ERRORED,
                    summary="Error retrieving root access key status.",
                    exception=str(e)
                )
            )

        return report
