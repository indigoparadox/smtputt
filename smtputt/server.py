
from email.message import EmailMessage
import logging
import email
import asyncore
from smtpd import SMTPServer
from threading import Thread
from importlib import import_module

from smtputt.channel import SMTPuttChannel

class SMTPuttServer( SMTPServer ):

    ''' SMTP listener. Listens for messages and dispatches them for
    processing. '''

    channel_class = SMTPuttChannel

    def __init__( self, module_cfgs, **kwargs ):

        self.logger = logging.getLogger( 'server' )
        self.thread : Thread
        self.module_cfgs = module_cfgs
        self.fixer_modules = [import_module( m ) \
            for m in kwargs['fixermodules'].split( ',' )] if \
            'fixermodules' in kwargs else []
        self.auth_modules = [import_module( m ) \
            for m in kwargs['authmodules'].split( ',' )] if \
            'authmodules' in kwargs else []
        self.relay_modules = [import_module( m ) \
            for m in kwargs['relaymodules'].split( ',' )] if \
            'relaymodules' in kwargs else []
        self.networks = kwargs['listennetworks'].split( ',' ) \
            if 'listennetworks' in kwargs else ['127.0.0.1/32']
        self.channels : 'list[SMTPuttChannel]'
        self.channels = []

        self.kwargs = kwargs

        self.listen_tuple = (
            kwargs['listenhost'] if 'listenhost' in kwargs else '0.0.0.0',
            int( kwargs['listenport'] ) if 'listenport' in kwargs else 25)

        super().__init__( self.listen_tuple, None )

    def fix_message( self, peer, msg : EmailMessage ):
        for module in self.fixer_modules:
            fixer = module.FIXER( **self.module_cfgs[module.__loader__.name] )
            msg = fixer.process_email( peer, msg )
        return msg

    def serve_thread( self, daemonize=False ):
        self.logger.info( 'starting server on %s...', self.listen_tuple )
        self.thread = Thread( target=asyncore.loop )
        self.thread.daemon = daemonize
        self.thread.start()
        return self.thread

    def handle_accepted(self, conn, addr):
        self.logger.debug( 'Incoming connection from %s', repr(addr) )
        channel = self.channel_class(
            self, conn, addr, self.data_size_limit, self._map,
            self.enable_SMTPUTF8, self._decode_data )
        self.channels.append( channel )

    def handle_close( self ):
        print( 'close' )
        super().handle_close()

    def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):

        self.logger.info( 'connection established by %s', peer )
        msg = email.message_from_string( data.decode( 'utf-8' ) )
        self.logger.info( 'incoming message from %s to %s',
            msg['From'], msg['To'] )

        msg = self.fix_message( peer, msg )

        for module in self.relay_modules:
            relay = module.RELAY( **self.module_cfgs[module.__loader__.name] )
            relay.send_email( msg )
