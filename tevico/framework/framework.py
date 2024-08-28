
from functools import reduce
import json
import os
from typing import List
from tevico.framework.configs.config import TevicoConfig
from tevico.framework.core.utils import CoreUtils
from tevico.framework.entities.provider.provider import Provider
from tevico.framework.entities.provider.provider_model import ProviderMetadata
from tevico.framework.entities.report.scan_model import ScanReport

class Framework():
    
    tevico_config: TevicoConfig
    
    core_utils: CoreUtils = CoreUtils()
    
    def __init__(self, config: TevicoConfig) -> None:
        self.tevico_config = config
    
    
    def __get_provider_metadata(self) -> List[ProviderMetadata]:
        """
        Retrieves the provider metadata for all modules and providers.
        Returns:
            List[ProviderMetadata]: A list of ProviderMetadata objects containing the package name and class name for each provider.
        """

        provider_metatdata: List[ProviderMetadata] = []
        
        module_list: List[str] = os.listdir('./modules')
        
        for module in module_list:
            module_provider_path = f'./modules/{module}/providers'
            
            for p in os.listdir(module_provider_path):
                if p.startswith('_') or p.startswith('.'):
                    continue
                
                module_provider_abspath = os.path.abspath(os.path.join(f'{module_provider_path}', f'{p}/provider.py'))    

                package_name = self.core_utils.get_package_name(module_provider_abspath)
                class_name = self.core_utils.get_class_name(module_provider_abspath)
                
                provider_metatdata.append(ProviderMetadata(package_name=package_name, class_name=class_name))
        
        return provider_metatdata
        
    
    def __get_providers(self) -> List[Provider]:
        """
        Retrieves a list of Provider objects based on the provider metadata.
        Returns:
            List[Provider]: A list of Provider objects.
        """
        
        providers: List[Provider] = []
        
        provider_metadata = self.__get_provider_metadata()
    
        for p in provider_metadata:
            provider = self.core_utils.get_provider_class(package_name=p.package_name, class_name=p.class_name)
            if provider is not None:
                providers.append(provider())

        return providers
        
    def run(self):
        """
        Executes the scanning process for all providers and generates a scan report.
        Returns:
            None
        Raises:
            Exception: If an error occurs during the scanning process.
        """
        
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
                print(f'\n❌ Error: {e}')
                os._exit(1)
        
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
        
        acc = reduce(accumulator, scans, { 'total': 0, 'success': 0, 'failed': 0 })
        
        print('\nScan Report Overview:')
        print(f'#️⃣  Total    : {acc['total']}')
        print(f'✅ Success  : {acc['success']}')
        print(f'❌ Failed   : {acc['failed']}')
        
        print(f'\n📄 Output written to: {OUTPUT_PATH}')
        print('\n👋👋👋 Bye!')
