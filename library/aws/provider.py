import os
import boto3

from typing import Any, Dict
from tevico.engine.configs.config import ConfigUtils
from tevico.engine.entities.provider.provider import Provider


class AWSProvider(Provider):
    
    __provider_name: str = 'AWS'
    
    def __init__(self) -> None:
        super().__init__(os.path.dirname(__file__))
    

    def connect(self) -> Any:
        aws_config = ConfigUtils().get_config().aws_config

        if aws_config is not None:
            return boto3.Session(profile_name=aws_config['profile'])
        
        return boto3.Session()

    @property
    def name(self) -> str:
        return self.__provider_name

    @property
    def metadata(self) -> Dict[str, str]:
        return {}

    @property
    def account_id(self) -> str:
        try:
            session = self.connect()
            sts_client = session.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            return account_id
        except Exception as e:
            return "Unknown"

    @property
def account_name(self) -> str:
    try:
        session = self.connect()
        
        # Try IAM account aliases first - works in most accounts with IAM permissions
        try:
            iam_client = session.client('iam')
            response = iam_client.list_account_aliases()
            aliases = response.get('AccountAliases', [])
            if aliases:
                return aliases[0]
        except Exception:
            pass
        
        # Try Account API as fallback
        try:
            account_client = session.client('account')
            response = account_client.get_account_information()
            account_name = response.get('AccountName')
            if account_name:
                return account_name
        except Exception:
            pass
            
        # If all else fails, return the account ID with a prefix
        return f"AWS Account {self.account_id}"
    except Exception:
        return "Unknown"