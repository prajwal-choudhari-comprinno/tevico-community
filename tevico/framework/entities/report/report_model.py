
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from tevico.framework.entities.scan.scan_model import ScanModel

class ReportModel(BaseModel):
    reports: list[ScanModel]
    pass_count: int
    fail_count: int

