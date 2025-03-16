import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class rds_instance_enhanced_monitoring_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        
        try:
            client = connection.client('rds')
            report.status = CheckStatus.PASSED
            instances = client.describe_db_instances()['DBInstances']
            
            for instance in instances:
                instance_name = instance['DBInstanceIdentifier']
                enhanced_monitoring = instance.get('EnhancedMonitoringResourceArn')
                
                if enhanced_monitoring:
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
