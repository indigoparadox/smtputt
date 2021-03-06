
import logging
import email
import asyncore
from smtpd import SMTPServer
from threading import Thread
from importlib import import_module

from smtputt.fixer import SMTPuttFixer
from smtputt.relay import SMTPuttRelay
from smtputt.channel import SMTPuttChannel

class SMTPuttServer( SMTPServer ):

    ''' SMTP listener. Listens for messages and dispatches them for
    processing. '''

    channel_class = SMTPuttChannel

    def __init__( self, **kwargs ):

        self.logger = logging.getLogger( 'server' )
        self.thread : Thread
        self.fixer = SMTPuttFixer( **kwargs )
        self.fixer.server = self
        self.relay = SMTPuttRelay( **kwargs )
        self.relay.server = self
        # TODO: Automatically add own network/loopback.
        self.networks = kwargs['listennetworks'].split( ',' ) \
            if 'listennetworks' in kwargs else ['127.0.0.1/32']

        if 'authmodule' in kwargs:
            kwargs['authmodule'] = import_module( kwargs['authmodule'] )

        self.kwargs = kwargs

        listen_tuple = (
            kwargs['listenhost'] if 'listenhost' in kwargs else '0.0.0.0',
            int( kwargs['listenport'] ) if 'listenport' in kwargs else 25)

        super().__init__( listen_tuple, None )

    def serve_thread( self, daemonize=False ):
        self.thread = Thread( target=asyncore.loop )
        self.thread.daemon = daemonize
        self.thread.start()
        return self.thread

    def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):

        self.logger.info( 'connection established by %s', peer )
        msg = email.message_from_string( data.decode( 'utf-8' ) )
        self.logger.info( 'incoming message from {} to {}'.format(
            msg['From'], msg['To'] ) )

        msg = self.fixer.process_email( peer, msg )
        self.relay.send_email( msg )
