"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-17
"""

import boto3
import tempfile
import os
import json
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import AwsResource, CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check
from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import transient_settings

class lambda_function_no_secrets_in_variables(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('lambda')
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED  # Default status
        report.resource_ids_status = []

        paginator = client.get_paginator('list_functions')

        try:
            for page in paginator.paginate():
                functions = page.get('Functions', [])
                
                for function in functions:
                    function_name = function['FunctionName']
                    function_arn = function['FunctionArn']

                    try:
                        response = client.get_function_configuration(FunctionName=function_name)
                        environment_variables = response.get('Environment', {}).get('Variables', {})

                        if not environment_variables:
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=AwsResource(arn=function_arn),
                                    status=CheckStatus.PASSED,
                                    summary=f"Lambda function {function_name} has no environment variables."
                                )
                            )
                            continue

                        # Convert environment variables to a formatted string for scanning
                        env_variables_data = "\n".join([f"{key}={value}" for key, value in environment_variables.items()])

                        # Scan for secrets
                        secrets_found = self.detect_secrets_scan(env_variables_data)

                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=function_arn),
                                status=CheckStatus.FAILED if secrets_found else CheckStatus.PASSED,
                                summary=f"Secrets {'found' if secrets_found else 'not found'} in {function_name}."
                            )
                        )

                        if secrets_found:
                            report.status = CheckStatus.FAILED  # Mark overall report as FAILED if any secrets are found

                    except Exception as e:
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=AwsResource(arn=function_arn),
                                status=CheckStatus.FAILED,
                                summary=f"Error scanning {function_name}: {str(e)}"
                            )
                        )
                        report.status = CheckStatus.FAILED

        except Exception as e:
            report.status = CheckStatus.FAILED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary=f"Unexpected error: {str(e)}"
                )
            )

        return report

    def detect_secrets_scan(self, data: str) -> bool:
        """
        Scans the given data for secrets using the detect-secrets library.
        Returns True if secrets are found, otherwise False.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as temp_data_file:
                temp_data_file.write(data)
                temp_data_file_path = temp_data_file.name

            secrets = SecretsCollection()

            settings = {
                "plugins_used": [
                    {"name": "ArtifactoryDetector"},
                    {"name": "AWSKeyDetector"},
                    {"name": "BasicAuthDetector"},
                    {"name": "CloudantDetector"},
                    {"name": "DiscordBotTokenDetector"},
                    {"name": "GitHubTokenDetector"},
                    {"name": "GitLabTokenDetector"},
                    {"name": "Base64HighEntropyString", "limit": 6.0},
                    {"name": "HexHighEntropyString", "limit": 3.0},
                    {"name": "IbmCloudIamDetector"},
                    {"name": "IbmCosHmacDetector"},
                    {"name": "JwtTokenDetector"},
                    {"name": "KeywordDetector"},
                    {"name": "MailchimpDetector"},
                    {"name": "NpmDetector"},
                    {"name": "OpenAIDetector"},
                    {"name": "PrivateKeyDetector"},
                    {"name": "PypiTokenDetector"},
                    {"name": "SendGridDetector"},
                    {"name": "SlackDetector"},
                    {"name": "SoftlayerDetector"},
                    {"name": "SquareOAuthDetector"},
                    {"name": "StripeDetector"},
                    {"name": "TwilioKeyDetector"},
                ],
                "filters_used": [
                    {"path": "detect_secrets.filters.common.is_invalid_file"},
                    {"path": "detect_secrets.filters.common.is_known_false_positive"},
                    {"path": "detect_secrets.filters.heuristic.is_likely_id_string"},
                    {"path": "detect_secrets.filters.heuristic.is_potential_secret"},
                ],
            }

            with transient_settings(settings):
                secrets.scan_file(temp_data_file_path)

            os.remove(temp_data_file_path)
            detect_secrets_output = json.dumps(secrets.json())
            return bool(json.loads(detect_secrets_output).get("results"))

        except Exception as e:
            return False
