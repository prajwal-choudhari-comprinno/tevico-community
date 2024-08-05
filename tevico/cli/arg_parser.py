
import textwrap
import argparse
from tevico.framework.core.enums import CommandsEnum
from tevico.framework.framework_handler import FrameworkHandler

def parse_args() -> None:
    epilog=textwrap.dedent("""
        Additional Help:
        Visit our GitHub page for more information - https://github.com/abhaynpai/tevico
        For enterprise edition of this platform visit - https://tevi.co
    """)
    
    parser = argparse.ArgumentParser(prog="tevico", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog)
    
    subparser = parser.add_subparsers(dest="command")
    
    init_subparser = subparser.add_parser('init')
    run_subparser = subparser.add_parser('run')
    
    # 
    install_subparser = subparser.add_parser('install')
    install_entity_subparser = install_subparser.add_subparsers(dest="entity")
    
    install_scan_subparser = install_entity_subparser.add_parser('scan')
    install_scan_subparser.add_argument('entity_name')
    
    install_platform_subparser = install_entity_subparser.add_parser('platform')
    install_platform_subparser.add_argument('entity_name')
    
    install_report_subparser = install_entity_subparser.add_parser('report')
    install_report_subparser.add_argument('entity_name')
    
    install_profile_subparser = install_entity_subparser.add_parser('profile')
    install_profile_subparser.add_argument('entity_name')
    
    install_channel_subparser = install_entity_subparser.add_parser('channel')
    install_channel_subparser.add_argument('entity_name')
    
    # 
    add_subparser_help = """
        The `add` command helps you add different entities in your setup.
    """
    add_subparser = subparser.add_parser('add', help=add_subparser_help)
    add_entity_subparser = add_subparser.add_subparsers(dest="entity")
    
    add_scan_subparser = add_entity_subparser.add_parser('scan')
    add_scan_subparser.add_argument('entity_name')
    
    add_platform_subparser = add_entity_subparser.add_parser('platform')
    add_platform_subparser.add_argument('entity_name')
    
    add_report_subparser = add_entity_subparser.add_parser('report')
    add_report_subparser.add_argument('entity_name')
    
    add_profile_subparser = add_entity_subparser.add_parser('profile')
    add_profile_subparser.add_argument('entity_name')
    
    add_channel_subparser = add_entity_subparser.add_parser('channel')
    add_channel_subparser.add_argument('entity_name')

    
    args = parser.parse_args()
    
    framework = FrameworkHandler()
    
    if args.command == CommandsEnum.init:
        return framework.handle_init(args=args)
    elif args.command == CommandsEnum.install:
        return framework.handle_install(args=args)
    elif args.command == CommandsEnum.add:
        return framework.handle_add(args=args)
    elif args.command == CommandsEnum.run:
        return framework.handle_run(args=args)
    else:
        return framework.handle_run(args=args)


