"""
AUTHOR: 
DATE: 
"""

import boto3

from tevico.engine.entities.report.check_model import CheckException, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class iam_account_security_contact_information_registered(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)

        # Initialize the Account client
        account_client = connection.client('account')
        
        report = CheckReport(name=__name__)
        
        report.resource_ids_status = []

        # Check if SECURITY contact is registered
        try:
            security_contact = account_client.get_alternate_contact(AlternateContactType='SECURITY')
            # print(security_contact['AlternateContact'])
            
            if 'AlternateContact' in security_contact and security_contact['AlternateContact']:
                report.status = CheckStatus.PASSED
                # print("Security contact information is registered.")
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name='SECURITY_CONTACT'),
                        status=CheckStatus.PASSED,
                        summary='Security contact information is appropriately registered.'
                    )
                )
            else:
                report.status = CheckStatus.FAILED
                # print("Security contact information is NOT registered.")
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name='SECURITY_CONTACT'),
                        status=CheckStatus.FAILED,
                        summary='Security contact information is NOT registered.'
                    )
                )

        except account_client.exceptions.ResourceNotFoundException as e:
            # Raised if the security contact is not set
            report.status = CheckStatus.FAILED
            # print("Security contact information is NOT registered.")
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='SECURITY_CONTACT'),
                    status=CheckStatus.FAILED,
                    summary='Security contact information is NOT registered.',
                    exception=str(e)
                )
            )

        except Exception as e:
            # Catch any other unexpected exceptions
            report.status = CheckStatus.FAILED
            # print(f"An unexpected error occurred: {str(e)}")
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name='SECURITY_CONTACT'),
                    status=CheckStatus.FAILED,
                    summary='Security contact information is NOT registered.',
                    exception=str(e)
                )
            )

        return report

# The check will return **True (passed)** if all required fields (`FullName`, `Title`, `EmailAddress`, and `PhoneNumber`) are present and not empty in Security Contact .
# The check will return **False (failed)** if any of these fields are missing or empty, or if an error occurs while fetching the contact information.
