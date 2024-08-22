
import importlib
import importlib.util
import os


class CoreUtils():
    
    def get_provider_class(self, package_name: str, class_name: str):
        module_spec = importlib.util.find_spec(package_name)
        
        if module_spec is not None:
            module_type = importlib.util.module_from_spec(module_spec)
            
            if module_spec.loader is not None:
                module_spec.loader.exec_module(module_type)
                cls = getattr(module_type, class_name)
                
                return cls
        
        return None
    
    # Given a python file path find its module name
    def get_module_name(self, file_path):
        # Get full path from the modules directory
        path = file_path.split(os.path.sep)
        path = path[path.index('modules'):]
        path[-1] = path[-1].replace('.py', '')
        print(path)
        return '.'.join(path)
    