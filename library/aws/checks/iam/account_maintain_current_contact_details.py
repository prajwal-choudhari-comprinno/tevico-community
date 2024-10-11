"""
AUTHOR: 
DATE: 11-10-2024
"""

import boto3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check


class CheckMetadata(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None


class FrameworkDimension(BaseModel):
    dimension_name: str
    dimension_value: str


class account_maintain_current_contact_details(Check):
    
    # Define the fields to check
    checks_to_perform: List[str] = ['full_name', 'phone_number', 'company_name', 'address', 'email', 
                                      'billing_contact', 'operations_contact', 'security_contact']

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)

        # Initialize IAM client
        iam_client = connection.client('iam')

        # List all IAM users
        users = iam_client.list_users()['Users']
        print(f"Total users found: {len(users)}")

        # Iterate over each user to check for billing contact information
        for user in users:
            username = user['UserName']
            print(f"Checking billing contact info for user: {username}")

            # Get user details
            billing_info = self.get_billing_contact_info(username)
            print(f"Billing info for {username}: {billing_info}")

            # Check required fields based on checks_to_perform
            missing_fields = [field for field in self.checks_to_perform if field in billing_info and not billing_info[field]]
            if not missing_fields:
                report.resource_ids_status[username] = True  # All contact info is present for this user
                print(f"✅ All contact information is present for user: {username}")
            else:
                report.passed = False  # Fail the check if any user has missing contact information
                report.resource_ids_status[username] = False  # Contact info is missing for this user
                print(f"❌ Missing contact information for user: {username}. Missing fields: {missing_fields}")

            # Check for alternate contacts
            alternate_contacts_info = self.get_alternate_contacts_info(username)
            print(f"Alternate contacts for {username}: {alternate_contacts_info}")

            # Check alternate contact fields based on checks_to_perform
            missing_alternate_contacts = [contact for contact in self.checks_to_perform if contact in alternate_contacts_info and not alternate_contacts_info[contact]]
            if missing_alternate_contacts:
                report.passed = False  # Fail the check if any alternate contact information is missing
                print(f"❌ Missing alternate contact information for user: {username}. Missing fields: {missing_alternate_contacts}")
            else:
                print(f"✅ All alternate contact information is present for user: {username}")

        # Add report metadata
        report.report_metadata = {
            'UserCount': len(users),
            'CheckedFields': self.checks_to_perform
        }
        print(f"Report generated with metadata: {report.report_metadata}")

        return report

    # Simulated function for fetching billing contact information
    def get_billing_contact_info(self, username: str) -> Dict[str, Optional[str]]:
        # Here we include the provided contact info for testing
        if username == "compirnno-Service":  # Example username for testing
            return {
                'full_name': "compirnno-Service",
                'phone_number': "+91-98863-01605",
                'company_name': "Comprinno",
                'address': "No. 77, 4th Cross, Reliable Tranquil Layout, Harlur Road, Bangalore, Karnataka 560102, IN",
                'email': "contact@comprinno.com"  # Assuming you have an email for testing
            }
        
        # Default return for other users, simulate missing info
        return {
            'full_name': None,
            'phone_number': None,
            'company_name': None,
            'address': None,
            'email': None
        }
    
    # Simulated function for fetching alternate contact information
    def get_alternate_contacts_info(self, username: str) -> Dict[str, Optional[str]]:
        # Here we simulate alternate contact information; you can replace this with actual logic
        if username == "compirnno-Service":  # Example username for testing
            return {
                'billing_contact': None,  # Simulate missing billing contact
                'operations_contact': None,  # Simulate missing operations contact
                'security_contact': None  # Simulate missing security contact
            }

        # Default return for other users, simulate all missing alternate contacts
        return {
            'billing_contact': None,
            'operations_contact': None,
            'security_contact': None
        }
