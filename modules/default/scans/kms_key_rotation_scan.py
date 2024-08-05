import boto3

from typing import Any, List
from tevico.framework.core.enums import FrameworkPillar
from tevico.framework.entities.scan.scan import Scan
from tevico.framework.entities.scan.scan_model import ScanModel


class KMSKeyRotationScan(Scan):
    
    __scan_name = 'aws_kms_key_rotation_scan'
    
    def __get_scan_model(self, platform: str, profile: str, framework_pillar: List[FrameworkPillar]) -> ScanModel:
        scan = ScanModel(
            name=self.__scan_name,
            platform=platform, profile=profile,
            framework_pillar=framework_pillar
        )
        
        scan.description = """Rotating AWS KMS keys is the process of periodically generating new encryption keys to replace old ones.This is a critical security best practice to mitigate the risk of compromised keys."""
        
        scan.success_message = """Hooray!!! All your keys are rotating on a timely basis."""
        
        scan.failure_message = """Oh Snap!!! Some of your keys are not rotated on a timely basis. You need to fix this ASAP! Check metadata for more insights."""
        
        return scan
    
    def execute(self, platform: str, profile: str, connection: boto3.Session, framework_pillar: List[FrameworkPillar]) -> ScanModel:
        # Initiate the scan model
        scan = self.__get_scan_model(
            platform=platform,
            profile=profile,
            framework_pillar=framework_pillar
        )
        
        # Define required variables for metadata and scan
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
                
                # If any one of the key has key rotation disabled then fail the scan
                if k_rot_status['KeyRotationEnabled'] is False:
                    scan.passed = False
             
        # Append key rotation status to metadata
        scan.metadata = {
            'key_rotation_status': key_rotation_status
        }
        
        return scan

