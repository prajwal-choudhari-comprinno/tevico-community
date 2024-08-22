
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from tevico.framework.core.enums import FrameworkDimension

######################################################################

class RemediationCode(BaseModel):
    """Remediation code for different platforms."""
    cli: str | None = Field(default=None, alias='CLI')
    native_iac: str | None = Field(default=None, alias='NativeIaC')
    other: str | None = Field(default=None, alias='Other')
    terraform: str | None = Field(default=None, alias='Terraform')


class RemediationRecommendation(BaseModel):
    """Recommendation for remediating the security check."""
    text: str = Field(..., alias='Text', description='Recommendation text')
    url: str | None = Field(default=None, alias='Url')  # Optional URL


class Remediation(BaseModel):
    """Remediation steps for the security check."""
    code: RemediationCode = Field(..., alias='Code', description='Remediation code for different platforms')
    recommendation: RemediationRecommendation = Field(..., alias='Recommendation', description='Recommendation for remediating the security check')


class ScanMetadata(BaseModel):
    """Pydantic model representing security scan metadata."""
    provider: str = Field(..., alias='Provider', description='Cloud provider (e.g., aws)')
    check_id: str = Field(..., alias='CheckID', description='Unique identifier for the check')
    check_title: str = Field(..., alias='CheckTitle', description='Title of the security check')
    check_aliases: list[str] | None = Field(alias='CheckAliases', default_factory=list, description='Alternative names for the check')
    check_type: list[str] = Field(..., alias='CheckType', description='List of check types')
    service_name: str = Field(..., alias='ServiceName', description='Cloud service involved in the check')
    sub_service_name: str = Field(..., alias='SubServiceName', description='Sub-service within the cloud service')
    resource_id_template: str = Field(..., alias='ResourceIdTemplate', description='Template for resource identification')
    severity: str = Field(..., alias='Severity', description='Severity level of the check (e.g., high, medium)')
    resource_type: str = Field(..., alias='ResourceType', description='Type of resource the check applies to')
    risk: str = Field(..., alias='Risk', description='Explanation of the security risk involved')
    related_url: str = Field(alias='RelatedUrl', default='', description='URL for further information')
    remediation: Remediation = Field(..., alias='Remediation', description='Steps to mitigate the security risk')
    categories: list[str] | None = Field(alias='Categories', default_factory=list, description='Categories associated with the check (e.g., forensics-ready)')
    depends_on: list[str] = Field(alias='DependsOn', default_factory=list, description='Checks this check depends on')
    related_to: list[str] = Field(alias='RelatedTo', default_factory=list, description='Related security checks')
    notes: str | None = Field(alias='Notes', default=None, description='Additional notes about the check')
    
    description: str = Field(..., alias='Description', description='Detailed description of the security check')
    success_message: Optional[str] = None
    failure_message: Optional[str] = None

######################################################################

class ScanReport(BaseModel):
    name: str
    passed: bool = True
    scan_metadata: ScanMetadata
    dimensions: List[FrameworkDimension]
    profile: Optional[str] = None
    resource_ids: Optional[str] = None
    report_metadata: Optional[Dict[str, Any]] = None
    created_on: datetime = datetime.now()
