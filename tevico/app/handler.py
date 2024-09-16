

import argparse
from tevico.app.main import TevicoFramework


class FrameworkHandler():
    
    framework: TevicoFramework
    
    def __init__(self) -> None:
        self.framework = TevicoFramework()

    def handle_run(self, args: argparse.Namespace):
        self.framework.run()
