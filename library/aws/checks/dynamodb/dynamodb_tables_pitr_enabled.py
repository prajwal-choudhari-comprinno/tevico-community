import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus
from tevico.engine.entities.check.check import Check


class dynamodb_tables_pitr_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('dynamodb')
        response = client.list_tables()
        tables = response['TableNames']

        report = CheckReport(name=__name__)
        report.status = CheckStatus.PASSED

        for table in tables:
            response = client.describe_continuous_backups(TableName=table)
            result = response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus'] == 'ENABLED'
            if not result:
                report.resource_ids_status[table]   = False
                report.status = CheckStatus.FAILED
            else:
                report.resource_ids_status[table] = True

        return report
