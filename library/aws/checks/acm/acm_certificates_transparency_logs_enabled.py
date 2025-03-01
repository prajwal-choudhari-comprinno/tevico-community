"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2025-01-09
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, AwsResource, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class acm_certificates_transparency_logs_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:

        # Initialize report and certificates list
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        report.resource_ids_status = []

        try:
            # Initialize ACM client
            client = connection.client('acm')
            certificates_found = False

            try:
                # List all ACM certificates using pagination
                paginator = client.get_paginator('list_certificates')
                for page in paginator.paginate():
                    certificates = page.get('CertificateSummaryList', [])

                    if certificates:
                        certificates_found = True

                    # Process each certificate
                    for cert in certificates:
                        cert_arn = cert.get('CertificateArn')

                        try:
                            # Get detailed certificate information
                            cert_details = client.describe_certificate(CertificateArn=cert_arn)
                            transparency_logging = cert_details.get('Certificate', {}).get('Options', {}).get('CertificateTransparencyLoggingPreference', 'ENABLED')

                            if transparency_logging != 'ENABLED':
                                report.resource_ids_status.append(
                                    ResourceStatus(
                                        resource=AwsResource(arn=cert_arn),
                                        status=CheckStatus.FAILED,
                                        summary="Certificate " + cert_arn + " has transparency logging disabled. "
                                    )
                                )                                
                                report.status = CheckStatus.FAILED
                            else:
                                report.resource_ids_status.append(
                                    ResourceStatus(
                                        resource=AwsResource(arn=cert_arn),
                                        status=CheckStatus.FAILED,
                                        summary="Certificate " + cert_arn + " has transparency logging enabled. "
                                    )
                                )                                

                        except Exception as e:
                            # Handle errors in getting certificate details
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=AwsResource(arn=cert_arn),
                                    status=CheckStatus.FAILED,
                                    summary="Error describing " + cert_arn + "."
                                )
                            )                                                            
                            report.status = CheckStatus.FAILED

            except Exception as e:
                # Handle errors in listing certificates
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.SKIPPED,
                        summary="ACM listing error.",
                        exception=str(e)
                    )
                )
                report.status = CheckStatus.FAILED

            if not certificates_found:
                # No certificates found, mark the check as passed
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=""),
                        status=CheckStatus.SKIPPED,
                        summary="No ACM certificates found."
                    )
                )                

        except Exception as e:
            # Handle any unexpected errors
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=""),
                    status=CheckStatus.FAILED,
                    summary="Unexpected error.",
                    exception=str(e)
                )
            )                
            report.status = CheckStatus.FAILED

        return report
