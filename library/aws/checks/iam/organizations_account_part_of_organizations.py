"""
AUTHOR: RONIT CHAUHAN
DATE: 11-10-24
"""

import boto3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from tevico.engine.entities.check.check import Check  # Import Check

# Define the CheckMetadata and FrameworkDimension if needed, assuming they exist in your codebase.
class CheckMetadata(BaseModel):
    name: str
    description: str

class FrameworkDimension(BaseModel):
    dimension_name: str
    dimension_value: str

# CheckReport Data Structure
class CheckReport(BaseModel):
    passed: bool = True
    name: str
    check_metadata: Optional[CheckMetadata] = None
    dimensions: List[FrameworkDimension] = []
    profile_name: Optional[str] = None
    resource_ids_status: Dict[str, bool] = {}
    report_metadata: Optional[Dict[str, Any]] = None
    created_on: datetime = datetime.now()

# Main class to check if an AWS account is part of any AWS organization
class organizations_account_part_of_organizations(Check):  # Inherit Check
    
    def execute(self, connection=None) -> CheckReport:
        # Initialize the report object
        report = CheckReport(
            passed=True,
            name="organizations_account_part_of_organizations",
            check_metadata=CheckMetadata(
                name="AWS Account Organization Check",
                description="Checks if the current AWS account is part of an AWS Organization."
            )
        )
        
        try:
            # Initialize AWS Organizations client
            organizations_client = boto3.client('organizations')
            sts_client = boto3.client('sts')  # For getting the account ID

            # Get the AWS account ID
            account_id = sts_client.get_caller_identity()['Account']

            # Attempt to describe the organization (if the account is part of one)
            try:
                org_info = organizations_client.describe_organization()
                
                # Organization is active, update the report
                org_id = org_info['Organization']['Id']
                org_name = org_info['Organization']['MasterAccountEmail']  # Organization name (master account email)
                report.resource_ids_status[org_id] = True
                report.passed = True
                report.report_metadata = {
                    "status": "PASS",
                    "details": f"Account {account_id} is part of AWS Organization with ID {org_id} and name {org_name}.",
                    "organization_id": org_id,
                    "organization_name": org_name,
                    "account_id": account_id
                }
                
                # Add debug info: successful check
                print(f"Account {account_id} is part of organization {org_name} (ID: {org_id}).")
                
            except organizations_client.exceptions.AWSOrganizationsNotInUseException:
                # Handle if the account is not part of any organization
                report.passed = False
                report.report_metadata = {
                    "status": "FAIL",
                    "details": f"Account {account_id} is not part of any AWS Organization.",
                    "account_id": account_id
                }
                
                # Add debug info: failed check
                print(f"Account {account_id} is not under any AWS Organization.")
                
            except Exception as e:
                # Handle general exception
                report.passed = False
                report.report_metadata = {
                    "status": "ERROR",
                    "details": f"Error occurred: {str(e)}",
                    "account_id": account_id
                }
                
                # Add debug info: error case
                print(f"Error for account {account_id}: {str(e)}")
                
        except Exception as e:
            # Handle exception in client initialization
            report.passed = False
            report.report_metadata = {
                "status": "ERROR",
                "details": f"Client initialization error: {str(e)}",
                "account_id": "Unknown"
            }
            
            # Add debug info: client initialization error
            print(f"Client initialization error: {str(e)}")

        # Return the final report
        return report
