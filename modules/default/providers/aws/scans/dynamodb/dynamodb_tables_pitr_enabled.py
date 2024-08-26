import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class dynamodb_tables_pitr_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        client = connection.client('dynamodb')
        response = client.list_tables()
        tables = response['TableNames']

        report = ScanReport(name=__name__)

        for table in tables:
            response = client.describe_continuous_backups(TableName=table)
            report.passed = response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus'] == 'ENABLED'
            report.resource_ids_status[table] = report.passed

        return report
