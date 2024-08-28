
import importlib
import importlib.util
import os
from typing import Optional


class CoreUtils():
    
    def get_provider_class(self, package_name: str, class_name: str):
        """
        Retrieves the class object from the specified package and class name.
        Args:
            package_name (str): The name of the package.
            class_name (str): The name of the class.
        Returns:
            Optional[Type[Any]]: The class object if found, otherwise None.
        """
        
        module_spec = importlib.util.find_spec(package_name)
        
        if module_spec is not None:
            module_type = importlib.util.module_from_spec(module_spec)
            
            if module_spec.loader is not None:
                module_spec.loader.exec_module(module_type)
                cls = getattr(module_type, class_name)
                
                return cls
        
        return None
    
    def get_package_name(self, file_path: str):
        """
        Returns the package name based on the given file path relative to the modules directory.
        Args:
            file_path (str): The path of the file.
        Returns:
            str: The package name.
        """
        
        path = file_path.split(os.path.sep)
        path = path[path.index('modules'):]
        path[-1] = path[-1].replace('.py', '')
        return '.'.join(path)
    
    
    def get_class_name(self, file_path: str) -> str:
        """
        Retrieves the name of the class defined in the given file.
        Args:
            file_path (str): The path to the file.
        Returns:
            str: The name of the class defined in the file. If no class is found, an empty string is returned.
        """
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'class' in line:
                    return line.split(' ')[1].split('(')[0]
            return ""