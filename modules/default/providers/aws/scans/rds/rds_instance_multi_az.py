import boto3

from tevico.framework.entities import report
from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class rds_instance_multi_az(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        report= ScanReport()
        client = connection.client('rds')
        response = client.describe_db_instances()
        for instance in response['DBInstances']:
            if not instance['MultiAZ']:
                report.passed = False
                report.resource_ids_status[instance['DBInstanceIdentifier']] = False
        return report
    