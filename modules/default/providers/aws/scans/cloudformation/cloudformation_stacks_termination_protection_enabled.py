import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class cloudformation_stacks_termination_protection_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        report = ScanReport()
        client = connection.client('cloudformation')
        stacks = client.list_stacks()['StackSummaries']
        for stack in stacks:
            stack_name = stack['StackName']
            
            try:
                stack_details = client.describe_stacks(StackName=stack_name)['Stacks'][0]
            except Exception as e:
                # print(f'Warning (Ignore): {e}')
                continue
            
            if stack_details['EnableTerminationProtection']:
                report.passed = True
                report.resource_ids_status[stack_details['StackId']] = True
            else:
                report.passed = False
                report.resource_ids_status[stack_details['StackId']] = False
        return report
