"""
AUTHOR: Ronit Chauhan
DATE: 11-10-2024
"""

import boto3
from typing import Dict, List, Optional
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class account_security_contact_information_registered(Check):
    # Define the fields to check
    security_checks_to_perform: List[str] = ['security_contact_name', 'security_contact_phone', 'security_contact_email']

    # Define metadata for the check
    check_title = "Account Security Contact Information Registered"
    service_name = "IAM"
    sub_service_name = "Account Management"
    resource_type = "User"
    risk = "High"
    description = "Ensures that all users have registered security contact information."
    remediation_recommendation = {
        "Text": "Please register the security contact information for the user."
    }

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__, title=self.check_title, service=self.service_name, sub_service=self.sub_service_name)

        iam_client = connection.client('iam')
        users = iam_client.list_users()['Users']
        print(f"Total users found: {len(users)}")

        for user in users:
            username = user['UserName']
            print(f"Checking security contact info for user: {username}")

            # Fetch security contact info for user
            security_info = self.get_security_contact_info(username)
            print(f"Security info for {username}: {security_info}")

            # Check required fields
            missing_fields = [field for field in self.security_checks_to_perform if field in security_info and not security_info[field]]
            if not missing_fields:
                report.resource_ids_status[username] = True
                print(f"✅ All security contact information is present for user: {username}")
            else:
                report.passed = False
                report.resource_ids_status[username] = False
                print(f"❌ Missing security contact information for user: {username}. Missing fields: {missing_fields}")

        # Add report metadata
        report.report_metadata = {
            'UserCount': len(users),
            'CheckedFields': self.security_checks_to_perform
        }
        print(f"Report generated with metadata: {report.report_metadata}")

        return report

    def get_security_contact_info(self, username: str) -> Dict[str, Optional[str]]:
        # Simulated function to fetch security contact information
        # Replace with actual logic to fetch this information
        return {
            'security_contact_name': None,  # Simulated value
            'security_contact_phone': None,
            'security_contact_email': None
        }
