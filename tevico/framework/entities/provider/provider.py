from abc import ABC, abstractmethod
from typing import List

from tevico.framework.entities.provider.provider_model import ProviderModel
from tevico.framework.entities.profile.profile_model import ProfileModel
from tevico.framework.entities.report.scan_model import ScanReport

class Provider(ABC):

    @property
    @abstractmethod
    def instance(self) -> ProviderModel:
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def define_profiles(self) -> List[ProfileModel]:
        raise NotImplementedError()
    
    @abstractmethod
    def execute_scans(self) -> List[ScanReport]:
        raise NotImplementedError()
    
    