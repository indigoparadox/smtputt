
import logging
import os
import argparse
import configparser

from smtputt.server import SMTPuttServer
from smtputt.fixer import SMTPuttFixer
from smtputt.relay import SMTPuttRelay

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument( '-c', '--config', action='store',
        default=os.path.join( os.getcwd(), 'smtputt.ini' ) )

    parser.add_argument( '-v', '--verbose', action='store_true' )

    args = parser.parse_args()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig( level=level )

    config = configparser.ConfigParser()
    config.read( args.config )

    relay_cfg = dict( config.items( 'forwarder' ) )
    relay = SMTPuttRelay( **kwargs )
    fixer_cfg = dict( config.items( 'fixer' ) )
    fixer = SMTPuttFixer( **fixer_cfg )

    server_cfg = dict( config.items( 'server' ) )
    server_cfg['relay'] = relay
    server_cfg['fixer'] = fixer
    
    cache = SMTPuttServer( **server_cfg )
    cache_thread = cache.serve_thread()
    cache_thread.join()

if '__main__' == __name__:
    main()
