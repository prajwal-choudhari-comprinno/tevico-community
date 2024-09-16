

import argparse
from tevico.app.configs.config import TevicoConfig
from tevico.app.configs.parser import ConfigParser
from tevico.app.core.enums import CommandsEnum
from tevico.app.framework import Framework


class FrameworkHandler():
    
    framework: Framework
    
    def __init__(self) -> None:
        config = self.get_config()
        self.framework = Framework(config=config)
    
    def get_config(self) -> TevicoConfig:
        parser = ConfigParser()
        config = parser.get_local_config()
        return config

    def handle_run(self, args: argparse.Namespace):
        # print(f'Command = {CommandsEnum.run}, {args}')
        
        self.framework.run()
