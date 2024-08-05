
from abc import ABC, abstractmethod
from typing import Any

from tevico.framework.entities.scan.scan_model import ScanModel


class Scan(ABC):
    
    @abstractmethod
    def execute(self, platform: str, profile: str, connection: Any) -> ScanModel:
        raise NotImplementedError()
    
    