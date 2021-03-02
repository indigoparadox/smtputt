
import asyncore
import logging
import os
import argparse
import configparser

from .server import SMTPuttServer

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

    cfg_dict = dict( config.items( 'forwarder' ) )

    cache = SMTPuttServer( **cfg_dict )

    asyncore.loop()

if '__main__' == __name__:
    main()
