

import argparse
from tevico.engine.configs.config import TevicoConfig
from tevico.engine.main import TevicoFramework


class FrameworkHandler():
    
    framework: TevicoFramework
    
    def __init__(self, ) -> None:
        self.framework = TevicoFramework()

    def handle_run(self) -> None:
        self.framework.run()
