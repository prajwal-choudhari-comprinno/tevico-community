import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class rds_instance_backup_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        report = ScanReport(name=__name__)
        client = connection.client('rds')
        instances = client.describe_db_instances()['DBInstances']
        for instance in instances:
            instance_name = instance['DBInstanceIdentifier']
            backup_retention_period = instance['BackupRetentionPeriod']
            if backup_retention_period == 0:
                report.passed = False
                report.resource_ids_status[instance_name] = False
            else:
                report.passed = True
                report.resource_ids_status[instance_name] = True
        return report

    