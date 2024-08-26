from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import os
from threading import Thread
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
    
    def handle_scan_execution(self, scan: Scan, profile_name: str) -> ScanReport:
        res = scan.get_report(profile_name=profile_name, connection=self.connection)
        
        if res is not None and res.passed:
            print(f'\t\t* Scan Passed ✅: {res.name}')
        else:
            print(f'\t\t* Scan Failed ❌: {res.name}')
        
        return res

    def execute_scans(self) -> List[ScanReport]:
        thread_pool = ThreadPoolExecutor(max_workers=5)
        scan_reports: List[ScanReport] = []
        futures = []

        for profile in self.profiles:
            print(f'\t* Load Profile ✅: {profile.name}')
            
            for scan in profile.scans:
                res = thread_pool.submit(self.handle_scan_execution, scan, profile.name)
                futures.append(res)
            
            scan_reports = [f.result() for f in futures]
            
        return scan_reports
    
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
            if cls is not None:
                return cls(metadata)
        
        return None

    def load_profiles(self) -> List[ProfileModel]:
        profiles: List[ProfileModel] = []
        
        profile_metadata_path = f'{self.provider_path}/metadata/profiles'
        
        if not self.is_connected:
            raise Exception('Provider is not connected')
        
        for file in os.listdir(profile_metadata_path):
            if file.endswith('yaml'):
                with open(os.path.join(profile_metadata_path, file), 'r') as f:
                    data = yaml.safe_load(f)
                    if 'scans' in data and isinstance(data['scans'], list):
                        scan_list = data['scans']
                        scans: List[Scan] = []
                        for scan_name in scan_list:
                            scan = self.load_scan(scan_name=scan_name)
                            if scan is not None:
                                scans.append(scan)
                        
                        data['scans'] = scans
                        
                    profile = ProfileModel(**data)
                    profiles.append(profile)
        
        return profiles
    
    