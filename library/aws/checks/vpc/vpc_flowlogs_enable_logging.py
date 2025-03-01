"""
AUTHOR: SUPRIYO BHAKAT
EMAIL: supriyo.bhakat@comprinno.net
DATE: 2024-11-12
"""

import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class vpc_flowlogs_enable_logging(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED
        ec2_client = connection.client('ec2')

        try:
            vpcs = ec2_client.describe_vpcs()
            for vpc in vpcs['Vpcs']:
                vpc_id = vpc['VpcId']
                response = ec2_client.describe_flow_logs(Filters=[{
                    'Name': 'resource-id',
                    'Values': [vpc_id]
                }]) 
                

                if not response['FlowLogs']:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=vpc_id),
                            status=CheckStatus.FAILED,
                            summary=''
                        )
                    )
                    report.status = CheckStatus.FAILED
                else:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=vpc_id),
                            status=CheckStatus.PASSED,
                            summary=''
                        )
                    )

            
        except Exception as e:
            report.status = CheckStatus.FAILED
        
        return report
