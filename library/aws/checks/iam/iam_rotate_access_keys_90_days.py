"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-14
"""

import boto3
import datetime

from tevico.engine.entities.report.check_model import AwsResource, CheckException, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class iam_rotate_access_keys_90_days(Check):

    def execute(self, connection: boto3.Session, maximum_key_age: int = 90) -> CheckReport:
        client = connection.client('iam')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []
        
        resource = GeneralResource(name='')
        arn = ''

        try:
            users = client.list_users().get('Users', [])

            if not users:
                report.status = CheckStatus.SKIPPED
                report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=""),
                            status=CheckStatus.SKIPPED,
                            summary=f"No IAM users found."
                        )
                    )
                return report

            for user in users:
                username = user['UserName']
                arn = user['Arn']
                resource = AwsResource(arn=arn)

                response = client.list_access_keys(UserName=username)
                access_keys = response.get('AccessKeyMetadata', [])

                if not access_keys:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=resource,
                            status=CheckStatus.SKIPPED,
                            summary=f"No access keys found."
                        )
                    )
                    continue

                for key in access_keys:
                    key_id = key['AccessKeyId']
                    status = key['Status']
                    create_date = key['CreateDate']

                    # Calculate key age
                    days_since_created = (datetime.datetime.now(tz=datetime.timezone.utc) - create_date).days
                    
                    if status == 'Inactive':
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED,
                                summary=f"Access Key {key_id} is inactive."
                            )
                        )
                    elif days_since_created > maximum_key_age:
                        # Key is outdated
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Access Key {key_id} is {status} but older than {maximum_key_age} days ({days_since_created} days old)."
                            )
                        )
                        report.status = CheckStatus.FAILED
                    else:
                        # Key is compliant
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED,
                                summary=f"Access Key {key_id} is {status} and compliant ({days_since_created} days old)."
                            )
                        )

        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=arn),
                    status=CheckStatus.ERRORED,
                    summary=f"Error occurred while checking access key rotation",
                    exception=str(e)
                )
            )
            
        return report
