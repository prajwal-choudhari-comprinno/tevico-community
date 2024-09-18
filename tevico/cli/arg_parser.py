
from tevico.engine.configs.config import ConfigUtils
from tevico.engine.handler import FrameworkHandler


def parse_args() -> None:
    ConfigUtils().get_config()
    
    framework = FrameworkHandler()
    
    return framework.handle_run()

