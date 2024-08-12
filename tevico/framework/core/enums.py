from enum import Enum

class CommandsEnum(str, Enum):
    config = 'config'
    init = 'init'
    install = 'install'
    add = 'add'
    run = 'run'
    
class EntitiesEnum(str, Enum):
    scan = 'scan'
    provider = 'provider'
    report = 'report'
    profile = 'profile'
    channel = 'channel'
    
class FrameworkDimension(str, Enum):
    cost = 'cost'
    operations = 'operations'
    performance = 'performance'
    reliability = 'reliability'
    security = 'security'
    sustainability = 'sustainability'
