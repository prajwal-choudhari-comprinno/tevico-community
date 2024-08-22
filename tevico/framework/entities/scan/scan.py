
from abc import ABC, abstractmethod
from typing import Any


from tevico.framework.entities.report.scan_model import ScanMetadata, ScanReport


class Scan(ABC):
    
    metadata: ScanMetadata
    
    def __init__(self, metadata: ScanMetadata) -> None:
        self.metadata = metadata
        super().__init__()
        
    def get_report(self, profile_name: str, connection: Any) -> ScanReport:
        scan_report = self.execute(connection=connection)
        scan_report.scan_metadata = self.metadata
        scan_report.profile_name = profile_name
        return scan_report
    
    @abstractmethod
    def execute(self, connection: Any) -> ScanReport:
        raise NotImplementedError()
    
    