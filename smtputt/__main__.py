
import logging
import argparse

from smtputt.config import load_config, load_or_create_config
from smtputt.server import SMTPuttServer

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument( '-c', '--config', action='store',
        help='Specify a path to a configuration file to use.' )

    parser.add_argument( '-n', '--create', action='store',
        help='If a valid configuration is not found, copy an example config.' )

    parser.add_argument( '-v', '--verbose', action='store_true',
        help='Show debugging log messages.' )

    parser.add_argument(
        '-o', '--option', action='append', nargs=3,
        metavar=('section', 'option', 'value'),
        help='specify a manual override for the given option' )

    args = parser.parse_args()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig( level=level )

    server_cfg = None
    module_cfgs = None

    if args.config:
        server_cfg, module_cfgs = load_config( args.config )

    else:
        server_cfg, module_cfgs = load_or_create_config( args.create )

    if args.option:
        for section, option, value in args.option:
            if 'server' == section:
                server_cfg[option] = value
            else:
                module_cfgs[section][option] = value

    cache = SMTPuttServer( module_cfgs, **server_cfg )
    cache_thread = cache.serve_thread()
    cache_thread.join()

if '__main__' == __name__:
    main()
