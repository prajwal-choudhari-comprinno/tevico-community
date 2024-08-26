
from functools import reduce
import importlib
import importlib.util
import json
from typing import List
from tevico.framework.configs.config import TevicoConfig
from tevico.framework.core.utils import CoreUtils
from tevico.framework.entities.provider.provider import Provider
from tevico.framework.entities.report.scan_model import ScanReport

class Framework():
    
    tevico_config: TevicoConfig
    
    core_utils: CoreUtils = CoreUtils()
    
    def __init__(self, config: TevicoConfig) -> None:
        self.tevico_config = config
    
    def __get_provider_class(self, package_name: str, class_name: str):
        module_spec = importlib.util.find_spec(package_name)
        
        if module_spec is not None:
            module_type = importlib.util.module_from_spec(module_spec)
            
            if module_spec.loader is not None:
                module_spec.loader.exec_module(module_type)
                cls = getattr(module_type, class_name)
                
                return cls
        
        return None
    
    def __get_module_list(self, path) -> List[str]:
        return []
    
    def __get_modules_from_local(self):
        pass
    
    def __get_modules_from_home(self):
        pass
    
    def __get_providers(self) -> List[Provider]:
        """Get Local Modules
        """
        providers: List[Provider] = []
        
        provider = self.core_utils.get_provider_class(package_name='modules.default.providers.aws.provider', class_name='AWSProvider')

        if provider is not None:
            providers.append(provider())
            
        return providers
        
    def run(self):
        providers = self.__get_providers()
        scans: List[ScanReport] = []
        
        OUTPUT_PATH = './tevico/report/data/output.json'
        
        for p in providers:
            try:
                print(f'\n* Running scans for provider 🚀: {p.name}')
                p.connect()
                result = p.execute_scans()
                scans.extend(result)
            except Exception as e:
                print(e)
        
        data = [s.model_dump(mode='json') for s in scans]
        
        with open(OUTPUT_PATH, 'w') as file:
            json.dump(data, file, indent=2)
            
        def accumulator(acc, scan):
            acc['total'] += 1
            if scan.passed:
                acc['success'] += 1
            else:
                acc['failed'] += 1
            return acc
        
        # Create a dictionary output that has 2 keys - 'success' and 'failed' using reduce on the scans list
        acc = reduce(accumulator, scans, { 'total': 0, 'success': 0, 'failed': 0 })
        
        print('\nScan Report Overview:')
        print(f'#️⃣  Total    : {acc['total']}')
        print(f'✅ Success  : {acc['success']}')
        print(f'❌ Failed   : {acc['failed']}')
        
        print(f'\n📄 Output written to: {OUTPUT_PATH}')
        print('\n👋👋👋 Bye!')
