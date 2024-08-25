import os
import boto3

from typing import Any, Dict, List
from modules.default.providers.aws.scans.iam.kms_key_rotation_scan import KMSKeyRotationScan
from tevico.framework.entities.provider.provider import Provider
from tevico.framework.entities.provider.provider_model import ProviderModel
from tevico.framework.entities.profile.profile_model import ProfileModel
from tevico.framework.entities.scan.scan import Scan
from tevico.framework.entities.report.scan_model import ScanReport


class AWSProvider(Provider):
    
    __provider_name: str = 'AWS'
    
    def __init__(self) -> None:
        super().__init__(os.path.dirname(__file__))
    

    @property
    def is_connected(self) -> bool:
        return self.is_connected

    def connect(self) -> Any:
        return boto3.Session(profile_name='ssg-prod')

    @property
    def name(self) -> str:
        return self.__provider_name

    @property
    def metadata(self) -> Dict[str, str]:
        return {}

