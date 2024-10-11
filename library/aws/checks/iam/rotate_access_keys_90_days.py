"""
AUTHOR: Mohd Asif
DATE: 11 oct 2024
"""


import boto3
from datetime import datetime, timedelta, timezone
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class rotate_access_keys_90_days(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
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
                        print(f"Access key for user {username} is older than 90 days and should be rotated.")
                        report.resource_ids_status[username] = True
                    else:
                        print(f"Access key for user {username} is within the 90-day limit.")
                        report.resource_ids_status[username] = False

            # Check if any users have access keys older than 90 days
            report.passed = not any(report.resource_ids_status.values())
        except Exception as e:
            print("Error in checking access key age for users")
            print(str(e))
            report.passed = False
        
        return report

