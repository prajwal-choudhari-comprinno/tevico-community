import json

from tevico.app.configs.config import TevicoConfig

class ConfigParser():
    
    def get_local_config(self) -> TevicoConfig:
        with open('tevico_config.json', 'r') as stream:
            data_loaded = json.load(stream)
            config = TevicoConfig.model_validate(data_loaded)
            return config
    
    def get_home_config(self):
        pass
    
