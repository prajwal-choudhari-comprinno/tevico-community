
from typing import Any
from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class apigatewayv2_api_access_logging_enabled(Scan):
    @property
    def name(self) -> str:
        raise NotImplementedError

    def execute(self, profile: str, connection: Any) -> ScanReport:
        raise NotImplementedError
