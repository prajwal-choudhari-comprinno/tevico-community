
import argparse
from enum import Enum
import textwrap
from typing import Dict, Optional
from pydantic import BaseModel

class EntitiesConfig(BaseModel):
    channels: Optional[list[str]]
    providers: Optional[list[str]]
    profiles: Optional[list[str]]
    checks: Optional[list[str]]

class ModuleLocation(str, Enum):
    local = 'local'
    home = 'home'

class EntityModuleMapping(BaseModel):
    module_name: str
    type: ModuleLocation
    entity_config: EntitiesConfig
    is_default: bool = False

class TevicoConfig(BaseModel):
    profile: Optional[str] = None
    aws_config: Optional[Dict[str, str]] = None


class ConfigUtils():
    def get_config_from_args(self, args: argparse.Namespace) -> TevicoConfig:
        config = TevicoConfig()
        
        if args.profile:
            config.profile = args.profile
        
        if args.aws_config:
            aws_config = {}

            for key_value in args.aws_config.split(','):
                key, value = key_value.split(':')
                aws_config[key] = value
            
            config.aws_config = aws_config
            
        return config
    
    def get_parser(self) -> argparse.ArgumentParser:
        epilog = textwrap.dedent("""
            Additional Help:
            Visit our GitHub page for more information - https://github.com/abhaynpai/tevico
            For enterprise edition of this provider visit - https://tevi.co
        """)
        
        parser = argparse.ArgumentParser(prog='tevico', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog)
        
        subparser = parser.add_subparsers(dest='command')
        
        run_parser = subparser.add_parser('run')
        
        run_parser.add_argument('--profile', help='The profile to run the checks against.', required=False)
        
        run_parser.add_argument('--aws_config', help='The AWS configuration to use for the checks.', required=False)
        
        return parser
    
    def get_config(self) -> TevicoConfig:
        return self.get_config_from_args(self.get_parser().parse_args())