
from smtputt.smtpcache import SMTPCache
import asyncore
import logging
import json

def main():
    logging.basicConfig( level=logging.INFO )

    config = {}
    with open( 'config.json', 'r' ) as config_file:
        config = json.loads( config_file.read() )

    cache = SMTPCache( (config['listen'], config['listen_port']),
        config['server'], config['port'], config['username'], config['password'] )

    asyncore.loop()

if '__main__' == __name__:
    main()
