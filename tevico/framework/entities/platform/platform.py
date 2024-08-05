from abc import ABC, abstractmethod
from typing import List

from tevico.framework.entities.platform.platform_model import PlatformModel
from tevico.framework.entities.platform.profile_model import ProfileModel
from tevico.framework.entities.scan.scan_model import ScanModel

class Provider(ABC):

    @property
    @abstractmethod
    def instance(self) -> PlatformModel:
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
    def execute_scans(self) -> List[ScanModel]:
        raise NotImplementedError()
    
    