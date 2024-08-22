import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class rds_instance_integration_cloudwatch_logs(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        raise NotImplementedError

    