"""
AUTHOR: Sheikh Aafaq Rashid
EMAIL: aafaq.rashid@comprinno.net
DATE: 2025-01-15
"""

import boto3
import base64
import re
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import (
    CheckReport, CheckStatus, GeneralResource, ResourceStatus
)
from tevico.engine.entities.check.check import Check


class ec2_launch_template_no_secrets(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        ec2_client = connection.client('ec2')
        report = CheckReport(name=__name__)
        report.resource_ids_status = []

        # Enhanced checks for sensitive data in launch template user data
        sensitive_keywords = [
            'password', 'secret', 'token', 'api_key', 'aws_secret_access_key',
            'aws_access_key_id', 'client_secret', 'username', 'credential', 
            'db_password', 'mysql_pass', 'postgres_pass', 'mongodb_pass'
        ]

        # Regular expressions for matching patterns
        regex_patterns = [
            r'(?i)(?:password\s*=\s*|(?<=\s))([A-Za-z0-9/+=]{20,})',  # Detecting passwords
            r'(?i)(?:api[-_.]?[Kk]ey|token|secret)[\s=:]*([A-Za-z0-9/+=]{20,})',  # API keys and tokens
            r'(?i)[A-Za-z0-9/+=]{32,}',  # Catching long random strings
            r'(?i)(aws_access_key_id|aws_secret_access_key|client_secret)[\s=:]*([A-Za-z0-9/+=]+)',  # AWS keys
        ]

        try:
            paginator = ec2_client.get_paginator('describe_launch_templates')
            has_templates = False

            for page in paginator.paginate():
                templates = page.get('LaunchTemplates', [])
                if templates:
                    has_templates = True

                for template in templates:
                    template_id = template['LaunchTemplateId']
                    versions = ec2_client.describe_launch_template_versions(
                        LaunchTemplateId=template_id
                    ).get('LaunchTemplateVersions', [])
                    
                    for version in versions:
                        user_data = version.get('LaunchTemplateData', {}).get('UserData')
                        if user_data:
                            decoded_user_data = base64.b64decode(user_data).decode('utf-8', errors='ignore')
                            
                            if any(keyword in decoded_user_data.lower() for keyword in sensitive_keywords) or \
                               any(re.search(pattern, decoded_user_data) for pattern in regex_patterns):
                                status = CheckStatus.FAILED
                                summary = f"Launch template {template_id} contains sensitive information in user data."
                            else:
                                status = CheckStatus.PASSED
                                summary = f"Launch template {template_id} does not contain sensitive information in user data."
                        else:
                            status = CheckStatus.PASSED
                            summary = f"Launch template {template_id} has no user data."

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name=template_id),
                                status=status,
                                summary=summary
                            )
                        )

            if not has_templates:
                report.status = CheckStatus.NOT_APPLICABLE
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.NOT_APPLICABLE,
                        summary="No EC2 launch templates found."
                    )
                )
                return report

        except (BotoCoreError, ClientError) as e:
            report.status = CheckStatus.UNKNOWN
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.UNKNOWN,
                    summary="Error retrieving EC2 launch template data.",
                    exception=str(e)
                )
            )

        return report
