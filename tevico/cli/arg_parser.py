
import textwrap
import argparse
from tevico.app.handler import FrameworkHandler

def parse_args() -> None:
    epilog=textwrap.dedent("""
        Additional Help:
        Visit our GitHub page for more information - https://github.com/abhaynpai/tevico
        For enterprise edition of this provider visit - https://tevi.co
    """)
    
    parser = argparse.ArgumentParser(prog='tevico', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog)
    
    subparser = parser.add_subparsers(dest='command')
    
    subparser.add_parser('run')
    
    args = parser.parse_args()
    
    framework = FrameworkHandler()
    
    return framework.handle_run(args=args)


