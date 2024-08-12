
from abc import ABC, abstractmethod
from typing import Any

from tevico.framework.entities.report.scan_model import ScanReport


class Scan(ABC):
    
    name: str
    
    @abstractmethod
    def execute(self, provider: str, profile: str, connection: Any) -> ScanReport:
        raise NotImplementedError()
    
    