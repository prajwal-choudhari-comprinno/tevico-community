from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Any, Dict, List

import yaml

from tevico.app.core.utils import CoreUtils
from tevico.app.entities.framework.framework_model import FrameworkModel
from tevico.app.entities.profile.profile_model import ProfileModel
from tevico.app.entities.report.check_model import CheckMetadata, CheckReport
from tevico.app.entities.check.check import Check

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
    
    def handle_check_execution(self, check: Check, profile_name: str) -> CheckReport:
        res = check.get_report(profile_name=profile_name, connection=self.connection)
        
        if res is not None and res.passed:
            print(f'\t\t* Check Passed ✅: {res.name}')
        else:
            print(f'\t\t* Check Failed ❌: {res.name}')
        
        return res

    def execute_checks(self) -> List[CheckReport]:
        thread_pool = ThreadPoolExecutor(max_workers=5)
        check_reports: List[CheckReport] = []
        futures = []

        for profile in self.profiles:
            print(f'\t* Load Profile ✅: {profile.name}')
            
            if profile.checks is not None:
                for check in profile.checks:
                    res = thread_pool.submit(self.handle_check_execution, check, profile.name)
                    futures.append(res)
            
            check_reports = [f.result() for f in futures]
            
        return check_reports

    def __get_metadata_path(self, check_name) -> str | None:
        file_name = f'{check_name}.yaml'
        
        for root, _, files in os.walk(self.provider_path):
            if file_name in files:
                return os.path.join(root, file_name)

        return None
    
    def __get_check_path(self, check_name) -> str | None:
        file_name = f'{check_name}.py'
        
        for root, _, files in os.walk(self.provider_path):
            if file_name in files:
                return os.path.join(root, file_name)
        
        return None
    
    def load_check(self, check_name: str) -> Check | None:
        metadata_path = self.__get_metadata_path(check_name=check_name)
        check_path = self.__get_check_path(check_name=check_name)
        
        metadata = None
        
        if metadata_path is not None:
            with open(metadata_path, 'r') as f:
                m = yaml.safe_load(f)
                metadata = CheckMetadata(**m)
                
        # print(f'Metadata = {metadata}')
        
        if check_path is not None:
            module_name = self.utils.get_package_name(check_path)
            cls = self.utils.get_provider_class(module_name, check_name)
            if cls is not None:
                return cls(metadata)
        
        return None

    def load_profiles(self) -> List[ProfileModel]:
        profiles: List[ProfileModel] = []
        
        profile_metadata_path: str = f'{self.provider_path}/metadata'
        
        if not self.is_connected:
            raise Exception(f'Provider ({self.name}) is not connected')
        
        for folder in os.listdir(profile_metadata_path):
            if folder.startswith('_') or folder.startswith('.'):
                continue
            
            framework_metadata_path = os.path.join(f'{profile_metadata_path}/{folder}', 'framework.yaml')
            
            with open(os.path.join(framework_metadata_path), 'r') as f_metadata:
                framework_raw_data = yaml.safe_load(f_metadata)
                framework_metadata = FrameworkModel(**framework_raw_data)
                
                profile_path = os.path.join(f'{profile_metadata_path}/{folder}/profiles', framework_metadata.default_profile)
                
                with open(os.path.join(profile_path), 'r') as f_profile:
                    profile_raw_data = yaml.safe_load(f_profile)
                    
                    if 'checks' in profile_raw_data and isinstance(profile_raw_data['checks'], list):
                        check_list = profile_raw_data['checks']
                        checks: List[Check] = []
                        for check_name in check_list:
                            check = self.load_check(check_name=check_name)
                            if check is not None:
                                checks.append(check)
                            
                        profile_raw_data['checks'] = checks
                    
                    profile = ProfileModel(**profile_raw_data)
                    profiles.append(profile)

        return profiles
    
    