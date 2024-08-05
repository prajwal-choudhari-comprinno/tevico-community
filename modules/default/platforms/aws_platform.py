import boto3

from typing import List
from modules.default.scans.kms_key_rotation_scan import KMSKeyRotationScan
from tevico.framework.entities.platform.platform import Provider
from tevico.framework.entities.platform.platform_model import PlatformModel
from tevico.framework.entities.platform.profile_model import ProfileModel
from tevico.framework.entities.scan.scan import Scan
from tevico.framework.entities.scan.scan_model import ScanModel


class AWSPlatform(Provider):
    
    _instance: PlatformModel
    
    __platform_name: str = 'AWS'
    
    def __init__(self) -> None:
        self._instance = PlatformModel(name=self.__platform_name, profiles=self.define_profiles())
    
    @property
    def instance(self) -> PlatformModel:
        return self._instance

    @property
    def is_connected(self) -> bool:
        return self.instance.is_connected

    def connect(self) -> None:
        self._instance.connection = boto3.Session(profile_name='ssg-prod')
        print(self._instance)

    def define_profiles(self) -> List[ProfileModel]:
        profiles: List[ProfileModel] = []
        
        cis_scans: List[Scan] = [
            KMSKeyRotationScan()
        ]
        
        cis_profile = ProfileModel(
            name='center_for_internet_security',
            scans=cis_scans
        )
        
        profiles.append(cis_profile)
        
        return profiles


    def execute_scans(self) -> List[ScanModel]:
        print(self._instance.profiles)
        result: List[ScanModel] = []
        for profile in self._instance.profiles:
            for scan in profile.scans:
                res = scan.execute(
                    platform=self.__platform_name,
                    profile=profile.name,
                    connection=self._instance.connection
                )
                
                result.append(res)
                
        return result