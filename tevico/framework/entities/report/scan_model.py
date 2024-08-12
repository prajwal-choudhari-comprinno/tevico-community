
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from tevico.framework.core.enums import FrameworkDimension

class ScanReport(BaseModel):
    name: str
    provider: str
    passed: bool = True
    framework_dimensions: List[FrameworkDimension]
    profile: Optional[str] = None
    description: Optional[str] = None
    success_message: Optional[str] = None
    failure_message: Optional[str] = None
    service_name: Optional[str] = ''
    resource_ids: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_on: datetime = datetime.now()
