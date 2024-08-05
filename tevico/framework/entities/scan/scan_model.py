
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from tevico.framework.core.enums import FrameworkPillar

class ScanModel(BaseModel):
    name: str
    platform: str
    passed: bool = True
    framework_pillar: List[FrameworkPillar]
    profile: Optional[str] = None
    description: Optional[str] = None
    success_message: Optional[str] = None
    failure_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_on: datetime = datetime.now()
