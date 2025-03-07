import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class rds_instance_multi_az(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        
        try:
            client = connection.client('rds')
            response = client.describe_db_instances()
            report.status = CheckStatus.PASSED 
            
            for instance in response['DBInstances']:
                instance_id = instance['DBInstanceIdentifier']
                multi_az = instance['MultiAZ']
                
                if not multi_az:
                    report.status = CheckStatus.FAILED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=instance_id),
                            status=CheckStatus.FAILED,
                            summary=''
                        )
                    )
                else:
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=instance_id),
                            status=CheckStatus.PASSED,
                            summary=''
                        )
                    )
                    
        except Exception as e:
            report.status = CheckStatus.FAILED
            return report

        return report
