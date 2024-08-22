import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class cloudtrail_cloudwatch_logging_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        raise NotImplementedError
