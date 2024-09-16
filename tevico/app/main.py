
from functools import reduce
import json
import os
from typing import List
from tevico.app.core.utils import CoreUtils
from tevico.app.entities.provider.provider import Provider
from tevico.app.entities.provider.provider_model import ProviderMetadata
from tevico.app.entities.report.check_model import CheckReport

class TevicoFramework():
    
    core_utils: CoreUtils = CoreUtils()
    
    
    def __get_provider_metadata(self) -> List[ProviderMetadata]:
        """
        Retrieves the provider metadata for all providers.
        Returns:
            List[ProviderMetadata]: A list of ProviderMetadata objects containing the package name and class name for each provider.
        """

        provider_metatdata: List[ProviderMetadata] = []
        
        provider_list: List[str] = os.listdir('./library')
        
        for provider in provider_list:
            try:
                module_provider_path = f'./library/{provider}'
                
                if provider.startswith('_') or provider.startswith('.'):
                    continue
                
                module_provider_abspath = os.path.abspath(os.path.join(f'{module_provider_path}', f'provider.py'))    

                package_name = self.core_utils.get_package_name(module_provider_abspath)
                class_name = self.core_utils.get_class_name(module_provider_abspath)
                
                provider_metatdata.append(ProviderMetadata(package_name=package_name, class_name=class_name))
                
            except Exception as e:
                # print(f'\n 🚨 Warning: {e}')
                pass
        
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
        Executes the checks for all providers and generates a report.
        Returns:
            None
        Raises:
            Exception: If an error occurs during the check execution process.
        """
        
        providers = self.__get_providers()
        checks: List[CheckReport] = []
        
        OUTPUT_PATH = './tevico/report/data/output.json'
        
        for p in providers:
            try:
                print(f'\n* Running checks for provider 🚀: {p.name}')
                p.connect()
                result = p.execute_checks()
                checks.extend(result)
            except Exception as e:
                print(f'\n❌ Error: {e}')
                os._exit(1)
        
        data = [s.model_dump(mode='json') for s in checks]
        
        with open(OUTPUT_PATH, 'w') as file:
            json.dump(data, file, indent=2)

        def accumulator(acc, check):
            acc['total'] += 1
            if check.passed:
                acc['success'] += 1
            else:
                acc['failed'] += 1
            return acc
        
        acc = reduce(accumulator, checks, { 'total': 0, 'success': 0, 'failed': 0 })
        
        print('\nReport Overview:')
        print(f'#️⃣  Total    : {acc['total']}')
        print(f'✅ Success  : {acc['success']}')
        print(f'❌ Failed   : {acc['failed']}')
        
        print(f'\n📄 Output written to: {OUTPUT_PATH}')
        print('\n👋👋👋 Bye!')
