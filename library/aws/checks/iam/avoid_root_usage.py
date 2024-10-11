"""
AUTHOR: 
DATE: 
"""

# import boto3

# from tevico.engine.entities.report.check_model import CheckReport
# from tevico.engine.entities.check.check import Check


# class avoid_root_usage(Check):

#     def execute(self, connection: boto3.Session) -> CheckReport:
#         report = CheckReport(name=__name__)

#         # Add your check logic here
        
#         return report


import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class avoid_root_usage(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')

        try:
            # Get the account's summary, which includes root usage
            account_summary = client.get_account_summary()['SummaryMap']
            root_last_used = account_summary.get('AccountAccessKeysPresent', 0) or account_summary.get('AccountMFAEnabled', 0)

            if root_last_used > 0:
                print("Root account has been used recently or root credentials are still active.")
                report.resource_ids_status['RootAccount'] = True  # Root usage detected
            else:
                print("Root account has not been used or no root credentials are active.")
                report.resource_ids_status['RootAccount'] = False  # No root usage
            
            # Pass if the root account has not been used
            report.passed = not report.resource_ids_status['RootAccount']

        except Exception as e:
            print("Error in checking root account usage")
            print(str(e))
            report.passed = False
        
        return report
