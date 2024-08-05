from enum import Enum

class CommandsEnum(str, Enum):
    config = 'config'
    init = 'init'
    install = 'install'
    add = 'add'
    run = 'run'
    
class EntitiesEnum(str, Enum):
    scan = 'scan'
    platform = 'platform'
    report = 'report'
    profile = 'profile'
    channel = 'channel'
    
class FrameworkPillar(str, Enum):
    cost = 'cost'
    operations = 'operations'
    performance = 'performance'
    reliability = 'reliability'
    security = 'security'
    sustainability = 'sustainability'
