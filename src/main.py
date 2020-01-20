
from smtputt.smtpcache import SMTPCache
import asyncore
import logging
import json
import os

def main():
    logging.basicConfig( level=logging.INFO )

    cfg_path = os.path.join( 'c:\\', 'program files', 'smtputt', 'src', 'config.json' )
    config = {}
    with open( cfg_path, 'r' ) as config_file:
        config = json.loads( config_file.read() )

    cache = SMTPCache( (config['listen'], config['listen_port']),
        config['server'], config['port'],
        config['username'], config['password'],
        config['from_addr'] )

    asyncore.loop()

if '__main__' == __name__:
    main()
