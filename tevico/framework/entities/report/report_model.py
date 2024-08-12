
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from tevico.framework.entities.report.scan_model import ScanReport

class ReportModel(BaseModel):
    reports: list[ScanReport]
    pass_count: int
    fail_count: int

