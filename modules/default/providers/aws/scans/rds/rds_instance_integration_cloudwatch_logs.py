import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class rds_instance_integration_cloudwatch_logs(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        report = ScanReport(name=__name__)
        client = connection.client('rds')
        instances = client.describe_db_instances()['DBInstances']
        for instance in instances:
            instance_name = instance['DBInstanceIdentifier']
            
            try:
                cloudwatch_logs = client.describe_db_log_files(DBInstanceIdentifier=instance_name)
            except Exception as e:
                # print(f'Warning (Ignore): {e}')
                continue
            
            if cloudwatch_logs:
                report.passed = True
                report.resource_ids_status[instance['DBInstanceIdentifier']] = True
            else:
                report.passed = False
                report.resource_ids_status[instance['DBInstanceIdentifier']] = False
        return report

    