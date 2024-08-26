
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from tevico.framework.entities.scan.scan import Scan

class ProfileModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    module_path: Optional[str] = None
    name: str
    scans: List[Scan] = []
