import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class rds_instance_backup_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        raise NotImplementedError

    