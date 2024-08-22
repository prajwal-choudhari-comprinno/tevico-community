
from abc import ABC, abstractmethod
from typing import Any


from tevico.framework.entities.report.scan_model import ScanMetadata, ScanReport


class Scan(ABC):
    
    metadata: ScanMetadata
    
    def __init__(self, metadata: ScanMetadata) -> None:
        self.metadata = metadata
        super().__init__()
        
    def get_report(self, profile: str, connection: Any) -> ScanReport:
        scan_report = self.execute(profile=profile, connection=connection)
        scan_report.scan_metadata = self.metadata
        return scan_report
    
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def execute(self, profile: str, connection: Any) -> ScanReport:
        raise NotImplementedError()
    
    