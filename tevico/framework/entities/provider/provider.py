from abc import ABC, abstractmethod
import os
from typing import Any, Dict, List

import yaml

from tevico.framework.core.utils import CoreUtils
from tevico.framework.entities.profile.profile_model import ProfileModel
from tevico.framework.entities.report.scan_model import ScanMetadata, ScanReport
from tevico.framework.entities.scan.scan import Scan

class Provider(ABC):
    
    provider_path: str
    utils: CoreUtils = CoreUtils()
    
    def __init__(self, path) -> None:
        self.provider_path = path
        super().__init__()
        
    """
    Already Implemented Properties
    """
    @property
    def profiles(self) -> List[ProfileModel]:
        return self.load_profiles()
    
    @property
    def connection(self) -> Any:
        return self.connect()
    
    
    """
    Abstract Properties
    """
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def metadata(self) -> Dict[str, str]:
        return {}

    @property
    def is_connected(self) -> bool:
        return self.connection is not None


    """
    Abstract methods
    """
    @abstractmethod
    def connect(self) -> Any:
        raise NotImplementedError()

    def execute_scans(self) -> List[ScanReport]:
        # print(self.profiles)
        result: List[ScanReport] = []
        for profile in self.profiles:
            for scan in profile.scans:
                res = scan.get_report(
                    profile_name=profile.name,
                    connection=self.connection
                )
                
                result.append(res)
                
        return result
    
    def __get_metadata_path(self, scan_name) -> str | None:
        file_name = f'{scan_name}.yaml'
        
        for root, _, files in os.walk(self.provider_path):
            if file_name in files:
                return os.path.join(root, file_name)

        return None
    
    def __get_scan_path(self, scan_name) -> str | None:
        file_name = f'{scan_name}.py'
        
        for root, _, files in os.walk(self.provider_path):
            if file_name in files:
                print(f'Path = {os.path.join(root, file_name)}')
                return os.path.join(root, file_name)
        
        return None
    
    def load_scan(self, scan_name) -> Scan | None:
        metadata_path = self.__get_metadata_path(scan_name=scan_name)
        scan_path = self.__get_scan_path(scan_name=scan_name)
        
        metadata = None
        
        if metadata_path is not None:
            with open(metadata_path, 'r') as f:
                m = yaml.safe_load(f)
                metadata = ScanMetadata(**m)
                
        # print(f'Metadata = {metadata}')
        
        if scan_path is not None:
            module_name = self.utils.get_module_name(scan_path)
            cls = self.utils.get_provider_class(module_name, scan_name)
            print(f'Class = {cls}')
            if cls is not None:
                return cls(metadata)
        
        return None

    def load_profiles(self) -> List[ProfileModel]:
        profiles: List[ProfileModel] = []
        
        profile_metadata_path = f'{self.provider_path}/metadata/profiles'
        
        for file in os.listdir(profile_metadata_path):
            print(f'File = {file}')
            if file.endswith('yaml'):
                with open(os.path.join(profile_metadata_path, file), 'r') as f:
                    data = yaml.safe_load(f)
                    if 'scans' in data and isinstance(data['scans'], list):
                        scan_list = data['scans']
                        scans: List[Scan] = []
                        for scan_name in scan_list:
                            print(f'Scan Name = {scan_name}')
                            scan = self.load_scan(scan_name=scan_name)
                            if scan is not None:
                                scans.append(scan)
                        
                        data['scans'] = scans
                        
                    profile = ProfileModel(**data)
                    profiles.append(profile)
        
        return profiles
    
    