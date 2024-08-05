
import importlib
import importlib.util
import json
from typing import List
from tevico.framework.configs.config import TevicoConfig
from tevico.framework.entities.platform.platform import Provider
from tevico.framework.entities.scan.scan_model import ScanModel

class Framework():
    
    tevico_config: TevicoConfig
    
    def __init__(self, config: TevicoConfig) -> None:
        self.tevico_config = config
    
    def __get_platform_class(self, module_name: str, class_name: str):
        module_spec = importlib.util.find_spec(module_name)
        
        if module_spec is not None:
            module_type = importlib.util.module_from_spec(module_spec)
            
            if module_spec.loader is not None:
                module_spec.loader.exec_module(module_type)
                cls = getattr(module_type, class_name)
                
                return cls
        
        return None
    
    def __get_modules_from_local(self):
        pass
    
    def __get_modules_from_home(self):
        pass
    
    def __get_platforms(self) -> List[Provider]:
        """Get Local Modules
        """
        platforms: List[Provider] = []
        # for module in self.tevico_config.modules:
        
        platform = self.__get_platform_class(module_name='modules.default.platforms.aws_platform', class_name='AWSPlatform')
        if platform is not None:
            platforms.append(platform())
            
        return platforms
        
    def run(self):
        platforms = self.__get_platforms()
        print(platforms)
        scans: List[ScanModel] = []
        for p in platforms:
            p.connect()
            result = p.execute_scans()
            scans.extend(result)
        
        print([s.model_dump_json() for s in scans])
