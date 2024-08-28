
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from tevico.framework.entities.report.check_model import CheckReport

class ReportModel(BaseModel):
    reports: list[CheckReport]
    pass_count: int
    fail_count: int

