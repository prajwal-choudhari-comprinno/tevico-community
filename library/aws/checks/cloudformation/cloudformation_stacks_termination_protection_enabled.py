import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class cloudformation_stacks_termination_protection_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
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
                report.status = CheckStatus.PASSED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=stack_details['StackId']),
                        status=CheckStatus.PASSED,
                        summary='Termination protection is enabled.'
                    )
                )
            else:
                report.status = CheckStatus.FAILED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=stack_details['StackId']),
                        status=CheckStatus.FAILED,
                        summary='Termination protection is not enabled.'
                    )
                )
        return report
