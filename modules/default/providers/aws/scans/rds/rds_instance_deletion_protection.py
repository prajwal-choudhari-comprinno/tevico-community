from typing import Any
from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class rds_instance_deletion_protection(Scan):
    @property
    def name(self) -> str:
        raise NotImplementedError

    def execute(self, profile: str, connection: Any) -> ScanReport:
        raise NotImplementedError

    