import boto3

from typing import Any, List
from tevico.app.core.enums import FrameworkDimension
from tevico.app.entities.check.check import Check
from tevico.app.entities.report.check_model import CheckReport


class KMSKeyRotationcheck(Check):
    
    __check_name = 'aws_kms_key_rotation_check'
    
    framework_dimensions = [FrameworkDimension.security]
    
    def __get_check_model(self, provider: str, profile: str) -> CheckReport:
        check = CheckReport(
            name=self.__check_name,
            provider=provider,
            profile=profile,
            dimensions=self.framework_dimensions
        )
        
        check.description = """Rotating AWS KMS keys is the process of periodically generating new encryption keys to replace old ones.This is a critical security best practice to mitigate the risk of compromised keys."""
        
        check.success_message = """Hooray!!! All your keys are rotating on a timely basis."""
        
        check.failure_message = """Oh Snap!!! Some of your keys are not rotated on a timely basis. You need to fix this ASAP! Check metadata for more insights."""
        
        return check
    
    def execute(self, connection: boto3.Session) -> CheckReport:
        # Initiate the check model
        check = self.__get_check_model(
            provider=provider,
            profile=profile
        )
        
        # Define required variables for metadata and check
        key_rotation_status = {}
        
        # Get client & list all keys
        client = connection.client('kms')
        pages = client.get_paginator('list_keys')
        
        # Get list of keys and check for each key check if rotation is enabled
        for res in pages.paginate():
            for key in res['Keys']:
                # Get the key ID
                key_id = key['KeyId']
                
                # Check if rotation is enabled for the key or not
                k_rot_status = client.get_key_rotation_status(KeyId=key_id)
                
                # Apply the status in the key rotation status dictionary
                key_rotation_status[key_id] = k_rot_status['KeyRotationEnabled']
                
                # If any one of the key has key rotation disabled then fail the check
                if k_rot_status['KeyRotationEnabled'] is False:
                    check.passed = False
             
        # Append key rotation status to metadata
        check.metadata = {
            'key_rotation_status': key_rotation_status
        }
        
        return check


