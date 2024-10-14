"""
AUTHOR: Mohd Asif <mohd.asif@comprinno.net>
DATE: 2024-10-10
"""


import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class support_role_created(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')
        try:
            # List all IAM roles
            roles = client.list_roles()['Roles']
            support_role_found = False
            
            for role in roles:
                role_name = role['RoleName']
                # Check if the role name indicates it is related to support
                if "support" in role_name.lower():
                    print(f"Support role found: {role_name}")
                    support_role_found = True
                    report.resource_ids_status[role_name] = True
            
            if not support_role_found:
                print("No support role found.")
                report.passed = False
            else:
                report.passed = True
            
        except Exception as e:
            print("Error in checking support roles")
            print(str(e))  # Log the error in the resource status
            report.passed = False
        
        return report
