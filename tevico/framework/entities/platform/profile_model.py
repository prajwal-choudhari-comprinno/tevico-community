
from typing import List
from pydantic import BaseModel, ConfigDict

from tevico.framework.entities.scan.scan import Scan

class ProfileModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    scans: List[Scan] = []
