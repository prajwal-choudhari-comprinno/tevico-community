

from typing import Any, Dict, List
from pydantic import BaseModel, field_validator

from tevico.framework.entities.platform.profile_model import ProfileModel


class PlatformModel(BaseModel):
    name: str
    profiles: List[ProfileModel] = []
    metadata: Dict[str, str] = {}
    connection: Any = None
    
    @property
    def is_connected(self) -> bool:
        return self.connection is not None
    
