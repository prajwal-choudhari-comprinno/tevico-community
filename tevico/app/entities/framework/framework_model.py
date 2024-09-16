

from pydantic import BaseModel


class FrameworkModel(BaseModel):
    name: str
    version: str
    description: str
    default_profile: str

