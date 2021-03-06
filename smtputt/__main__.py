
import logging
import os
import argparse
import configparser

from smtputt.server import SMTPuttServer

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

    module_cfgs = {}
    server_cfg = dict( config.items( 'server' ) )
    for module in server_cfg['authmodules'].split( ',' ):
        module_cfgs[module] = dict( config.items( module ) )
    for module in server_cfg['relaymodules'].split( ',' ):
        module_cfgs[module] = dict( config.items( module ) )
    for module in server_cfg['fixermodules'].split( ',' ):
        module_cfgs[module] = dict( config.items( module ) )

    cache = SMTPuttServer( module_cfgs, **server_cfg )
    cache_thread = cache.serve_thread()
    cache_thread.join()

if '__main__' == __name__:
    main()
