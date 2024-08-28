import os
import boto3

from typing import Any, Dict
from tevico.framework.entities.provider.provider import Provider


class AWSProvider(Provider):
    
    __provider_name: str = 'AWS'
    
    def __init__(self) -> None:
        super().__init__(os.path.dirname(__file__))
    

    def connect(self) -> Any:
        return boto3.Session(profile_name='ssg-prod')

    @property
    def name(self) -> str:
        return self.__provider_name

    @property
    def metadata(self) -> Dict[str, str]:
        return {}

