"""
AUTHOR: Deepak Puri
EMAIL: deepak.puri@comprinno.net
DATE: 2024-10-11
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class iam_root_hardware_mfa_enabled(Check):
    
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.resource_ids_status = []
        resource_id = "root"
        iam_client = connection.client("iam")
        
        try:
            # Fetch account summary to check if any MFA is enabled for the root account
            account_summary = iam_client.get_account_summary()['SummaryMap']
            
            if account_summary['AccountMFAEnabled'] != 1:
                # MFA is not enabled for root, immediately fail the check
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=resource_id),
                        status=CheckStatus.FAILED,
                        summary='MFA itself is not enabled for the root account.'
                    )
                )
                return report
            
            # Check if root account is using a virtual MFA device
            virtual_mfa_devices = self._list_virtual_mfa_devices(connection)
            for mfa_device in virtual_mfa_devices:
                if "root" in mfa_device.get("User", {}).get("Arn", ""):
                    report.status = CheckStatus.FAILED  # Root is using virtual MFA, fail the hardware check
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=resource_id),
                            status=CheckStatus.FAILED,
                            summary='Root is using virtual MFA.'
                        )
                    )
                    return report

            # If no virtual MFA for the root account, pass for hardware MFA
            report.status = CheckStatus.PASSED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=resource_id),
                    status=CheckStatus.PASSED,
                    summary='Root is using hardware MFA.'
                )
            )
        
        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=resource_id),
                    status=CheckStatus.ERRORED,
                    summary='An unknown exception has occurred during the execution of this check.'
                )
            )

        return report

    def _list_virtual_mfa_devices(self, connection: boto3.Session):
        mfa_devices = []
        try:
            client = connection.client("iam")
            list_virtual_mfa_devices_paginator = client.get_paginator("list_virtual_mfa_devices")

            for page in list_virtual_mfa_devices_paginator.paginate():
                mfa_devices.extend(page.get("VirtualMFADevices", []))
        except Exception as e:
            pass  

        return mfa_devices
