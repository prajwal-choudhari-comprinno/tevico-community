
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class EntitiesConfig(BaseModel):
    channels: Optional[list[str]]
    platforms: Optional[list[str]]
    profiles: Optional[list[str]]
    scans: Optional[list[str]]

class ModuleLocation(str, Enum):
    local = 'local'
    home = 'home'

class EntityModuleMapping(BaseModel):
    module_name: str
    type: ModuleLocation
    entity_config: EntitiesConfig
    is_default: bool = False

class TevicoConfig(BaseModel):
    modules: list[str] = ['default']
    exclude_entities: Optional[EntitiesConfig] = None

