# """
# AUTHOR: RONIT CHAUHAN 
# DATE: 2024-10-11
# """

# import boto3
# from typing import List, Dict, Optional, Any
# from datetime import datetime
# from tevico.engine.entities.report.check_model import CheckReport
# from tevico.engine.entities.check.check import Check

# class account_maintain_current_contact_details(Check):

#     def execute(self, connection: boto3.Session) -> CheckReport:
#         report = CheckReport(name=__name__)
#         print("Starting the account contact details check...")

#         # List of attributes to check
#         checks_to_perform: List[str] = [
#             'full_name', 'phone_number', 'company_name', 'address', 'email',  
#         ]
        
#         print("Attributes to check:", checks_to_perform)

#         # Get the current account information from AWS
#         client = connection.client('account')

#         try:
#             # Fetch account contact details using the AWS Account API
#             print("Fetching account contact information...")
#             contact_info = client.get_contact_information()
#             print("Contact information fetched successfully.")
#             print("Raw response:", contact_info)  # Debugging line
            
#             # Extract relevant fields from the fetched information
#             account_details = {
#                 'full_name': contact_info.get('FullName'),
#                 'phone_number': contact_info.get('PhoneNumber'),
#                 'company_name': contact_info.get('CompanyName'),
#                 'address': contact_info.get('AddressLine1'),  # assuming primary address field
#                 'email': contact_info.get('EmailAddress'),
#                 'billing_contact': contact_info.get('BillingContact'), 
#                 'operations_contact': contact_info.get('OperationsContact'), 
#                 'security_contact': contact_info.get('SecurityContact')
#             }

#             print("Account details retrieved:", account_details)

#             # Compare the retrieved account details with the checks_to_perform list
#             all_checks_passed = True
#             for check in checks_to_perform:
#                 if not account_details.get(check):
#                     print(f"Check failed: '{check}' is missing or empty.")
#                     all_checks_passed = False
#                     report.resource_ids_status[check] = False
#                 else:
#                     print(f"Check passed: '{check}' is present.")
#                     report.resource_ids_status[check] = True

#             # Set the final report status based on whether all checks passed
#             report.passed = all_checks_passed
#             if report.passed:
#                 print("All checks passed successfully.")
#             else:
#                 print("Some checks failed.")

#         except client.exceptions.NoSuchEntityException:
#             # Handle the case where contact information cannot be found
#             report.passed = False
#             report.report_metadata = {"error": "No contact information found for this account"}
#             print("Error: No contact information found for this account.")
        
#         except Exception as e:
#             # Handle any other exceptions
#             report.passed = False
#             report.report_metadata = {"error": str(e)}
#             print(f"An unexpected error occurred: {e}")

#         print("Check execution completed.")
#         return report
