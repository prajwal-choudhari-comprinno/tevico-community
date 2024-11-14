"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-14
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
from botocore.exceptions import ClientError

class cloudfront_access_logging_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('cloudfront')
        report = CheckReport(name=__name__)
        report.passed = True

        try:
            distributions = client.list_distributions()

            if 'DistributionList' in distributions:
                items = distributions['DistributionList'].get('Items', [])
                if items:  
                    for distribution in items:
                        dist_id = distribution['Id']
                        dist_logging = distribution['Logging']

                        if dist_logging['Enabled']:
                            report.resource_ids_status[dist_id] = True
                        else:
                            report.resource_ids_status[dist_id] = False
                            report.passed = False
                            
        except ClientError:
            report.passed = False
            
        return report
