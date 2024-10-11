"""
AUTHOR: Ronit Chauhan
DATE: 11-10-2024
"""

import boto3
from typing import Dict, List, Optional
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check


class account_security_questions_registered(Check):
    # Define the fields to check
    security_checks_to_perform: List[str] = ['security_question_1', 'security_question_2']

    # Define metadata for the check
    check_title = "Account Security Questions Registered"
    service_name = "IAM"
    sub_service_name = "Account Management"
    resource_type = "User"
    risk = "Medium"
    description = "Ensures that all users have registered security questions."
    remediation_recommendation = {
        "Text": "Please register the security questions for the user."
    }

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__, title=self.check_title, service=self.service_name, 
                             sub_service=self.sub_service_name)

        iam_client = connection.client('iam')
        users = iam_client.list_users()['Users']
        print(f"Total users found: {len(users)}")

        for user in users:
            username = user['UserName']
            print(f"Checking security questions for user: {username}")

            # Fetch security question info for user
            security_info = self.get_security_question_info(username)
            print(f"Security question info for {username}: {security_info}")

            # Check required fields
            missing_fields = [field for field in self.security_checks_to_perform if field in security_info and not security_info[field]]
            if not missing_fields:
                report.resource_ids_status[username] = True
                print(f"✅ All security questions are registered for user: {username}")
            else:
                report.passed = False
                report.resource_ids_status[username] = False
                print(f"❌ Missing security questions for user: {username}. Missing fields: {missing_fields}")

        # Add report metadata
        report.report_metadata = {
            'UserCount': len(users),
            'CheckedFields': self.security_checks_to_perform
        }
        print(f"Report generated with metadata: {report.report_metadata}")

        return report

    def get_security_question_info(self, username: str) -> Dict[str, Optional[str]]:
        # Simulated function to fetch security question information
        # Replace with actual logic to fetch this information
        return {
            'security_question_1': None,  # Simulated value
            'security_question_2': None   # Simulated value
        }
