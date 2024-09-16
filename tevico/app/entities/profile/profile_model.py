
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from tevico.app.entities.check.check import Check

class ProfileModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    module_path: Optional[str] = None
    name: str
    checks: List[Check] = []
