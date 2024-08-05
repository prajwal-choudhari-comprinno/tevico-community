

import argparse
from tevico.framework.configs.config import TevicoConfig
from tevico.framework.configs.parser import ConfigParser
from tevico.framework.core.enums import CommandsEnum
from tevico.framework.framework import Framework


class FrameworkHandler():
    
    framework: Framework
    
    def __init__(self) -> None:
        config = self.get_config()
        self.framework = Framework(config=config)
    
    def get_config(self) -> TevicoConfig:
        parser = ConfigParser()
        config = parser.get_local_config()
        return config
    
    def handle_init(self, args: argparse.Namespace):
        print(f'Command = {CommandsEnum.init}, {args}')

    def handle_install(self, args: argparse.Namespace):
        print(f'Command = {CommandsEnum.install}, {args}')

    def handle_add(self, args: argparse.Namespace):
        print(f'Command = {CommandsEnum.add}, {args}')

    def handle_run(self, args: argparse.Namespace):
        print(f'Command = {CommandsEnum.run}, {args}')
        
        self.framework.run()
