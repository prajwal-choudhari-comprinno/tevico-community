
from abc import ABC, abstractmethod
from typing import Any


from tevico.app.entities.report.check_model import CheckMetadata, CheckReport


class Check(ABC):
    
    metadata: CheckMetadata
    
    def __init__(self, metadata: CheckMetadata) -> None:
        self.metadata = metadata
        super().__init__()
        
    def get_report(self, profile_name: str, connection: Any) -> CheckReport:
        check_report = self.execute(connection=connection)
        check_report.check_metadata = self.metadata
        check_report.profile_name = profile_name
        return check_report
    
    @abstractmethod
    def execute(self, connection: Any) -> CheckReport:
        raise NotImplementedError()
    
    