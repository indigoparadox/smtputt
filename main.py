
from smtputt.smtpcache import SMTPCache
import asyncore
import logging
import json
import os
import argparse
import configparser

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

    #cfg_path = os.path.join( 'c:\\', 'program files', 'smtputt', 'src', 'config.json' )
    #config = {}
    #with open( cfg_path, 'r' ) as config_file:
    #    config = json.loads( config_file.read() )

    cfg_dict = dict( config.items( 'forwarder' ) )

    cache = SMTPCache( **cfg_dict )
    #(config['listen'], config['listen_port']),
    #    config['server'], config['port'],
    #    config['username'], config['password'],
    #    config['from_addr'] )

    asyncore.loop()

if '__main__' == __name__:
    main()
