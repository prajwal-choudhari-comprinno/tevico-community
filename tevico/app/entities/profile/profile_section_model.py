
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from tevico.app.entities.check.check import Check

class ProfileSection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    description: str
    checks: Optional[List[Check]] = []
