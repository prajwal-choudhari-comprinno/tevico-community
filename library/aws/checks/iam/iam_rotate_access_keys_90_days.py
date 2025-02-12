"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-14
"""

import boto3
import datetime
import pytz

from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, ResourceStatus, GeneralResource
from tevico.engine.entities.check.check import Check


class iam_rotate_access_keys_90_days(Check):

    def execute(self, connection: boto3.Session, maximum_key_age: int = 90) -> CheckReport:
        client = connection.client('iam')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            users = client.list_users()['Users']

            for user in users:
                username = user['UserName']
                arn = user['Arn']
                resource = AwsResource(arn=arn)

                response = client.list_access_keys(UserName=username)
                access_keys = response['AccessKeyMetadata']

                for key in access_keys:
                    key_id = key['AccessKeyId']
                    status = key['Status']
                    create_date = key['CreateDate']

                    # Calculate key age
                    days_since_created = (datetime.datetime.now(pytz.utc) - create_date).days

                    if status == 'Active' and days_since_created > maximum_key_age:
                        # Key is outdated
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.FAILED,
                                summary=f"Access Key {key_id} is active but older than {maximum_key_age} days ({days_since_created} days old)."
                            )
                        )
                        report.status = CheckStatus.FAILED
                    elif status == 'Active':
                        # Key is compliant
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED,
                                summary=f"Access Key {key_id} is active and compliant ({days_since_created} days old)."
                            )
                        )
                    else:
                        # Key is inactive
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=resource,
                                status=CheckStatus.PASSED,
                                summary=f"Access Key {key_id} is inactive."
                            )
                        )

        except Exception as e:
            report.status = CheckStatus.ERRORED
            report.report_metadata = {"error": str(e)}
            
        return report
