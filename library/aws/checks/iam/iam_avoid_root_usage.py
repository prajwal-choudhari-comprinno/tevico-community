"""
AUTHOR: Mohd Asif <mohd.asif@comprinno.net>
DATE: 2024-10-10
"""

import boto3
from datetime import datetime, timezone
from dateutil import parser
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

# Define maximum number of days allowed for root access
maximum_access_days = 1

class iam_avoid_root_usage(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')
        
        report.resource_ids_status = []

        try:
            # Generate the credential report
            client.generate_credential_report()
            response = client.get_credential_report()['Content']
            decoded_report = response.decode('utf-8').splitlines()

            # Parse the CSV-like credential report
            for row in decoded_report[1:]:
                user_info = row.split(',')
                if user_info[0] == "<root_account>":
                    # Extract last access times
                    password_last_used = user_info[4]
                    access_key_1_last_used = user_info[6]
                    access_key_2_last_used = user_info[9]

                    last_accessed = None

                    # Check when the root account was last accessed (password or access keys)
                    if password_last_used != "not_supported":
                        last_accessed = parser.parse(password_last_used)
                    elif access_key_1_last_used != "N/A":
                        last_accessed = parser.parse(access_key_1_last_used)
                    elif access_key_2_last_used != "N/A":
                        last_accessed = parser.parse(access_key_2_last_used)

                    if last_accessed:
                        days_since_accessed = (datetime.now(timezone.utc) - last_accessed).days

                        # Evaluate against maximum access days
                        if days_since_accessed <= maximum_access_days:
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=GeneralResource(name='RootAccount'),
                                    status=CheckStatus.FAILED,
                                    summary='Root account was recently accessed.'
                                )
                            )
                            report.status = CheckStatus.FAILED
                        else:
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=GeneralResource(name='RootAccount'),
                                    status=CheckStatus.PASSED,
                                    summary=f'Root account was last accessed {days_since_accessed} days ago.'
                                )
                            )
                            report.status = CheckStatus.PASSED
                    else:

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name='RootAccount'),
                                status=CheckStatus.PASSED,
                                summary=f'Root account was not recently accessed.'
                            )
                        )
                        report.status = CheckStatus.PASSED

                    break  # We only care about the root account, so stop after processing

        except Exception as e:

            report.status = CheckStatus.FAILED
            
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='RootAccount'),
                    status=CheckStatus.ERRORED,
                    summary='Error processing iam_avoid_root_usage check',
                    exception=str(e)
                )
            )

        return report
