import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class rds_instance_deletion_protection(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        
        try:
            client = connection.client('rds')
            instances = client.describe_db_instances()['DBInstances']
            report.status = CheckStatus.PASSED
            
            for instance in instances:
            
                instance_name = instance['DBInstanceIdentifier']
                
                if instance['DeletionProtection']:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=instance_name),
                            status=CheckStatus.PASSED,
                            summary=''
                        )
                    )
                else:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=instance_name),
                            status=CheckStatus.FAILED,
                            summary=''
                        )
                    )
                         
        except Exception as e:
            report.status = CheckStatus.FAILED
            return report

        return report

    