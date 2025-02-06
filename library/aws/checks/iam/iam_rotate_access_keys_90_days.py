"""
AUTHOR: Mohd Asif <mohd.asif@comprinno.net>
DATE: 2024-10-10
"""


import boto3
from datetime import datetime, timedelta, timezone
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus
from tevico.engine.entities.check.check import Check

class iam_rotate_access_keys_90_days(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        client = connection.client('iam')

        try:
            # Get the current date and time as an aware datetime object
            current_time = datetime.now(timezone.utc)
            # Define the 90-day threshold
            ninety_days_ago = current_time - timedelta(days=90)

            # List all IAM users
            users = client.list_users()['Users']
            for user in users:
                username = user['UserName']
                # List access keys for each user
                access_keys = client.list_access_keys(UserName=username)['AccessKeyMetadata']
                
                for key in access_keys:
                    create_date = key['CreateDate']  # AWS returns this as a timezone-aware datetime
                    
                    # Compare access key creation date to the 90-day threshold
                    if key['Status'] == 'Active' and create_date < ninety_days_ago:

                        report.resource_ids_status[username] = True
                    else:

                        report.resource_ids_status[username] = False
                        report.status = CheckStatus.FAILED

            # Check if any users have access keys older than 90 days
        except Exception as e:

            report.status = CheckStatus.FAILED
        
        return report

