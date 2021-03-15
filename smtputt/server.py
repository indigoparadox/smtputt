
from email.message import EmailMessage
import logging
import email
import struct
import socket
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
        self.mynetworks = \
            [tuple( n.split( '/' ) ) for \
                n in kwargs['mynetworks'].split( ',' )] if \
            'mynetworks' in kwargs else [('127.0.0.0', '8'), ('::1', '128')]
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
        #print( 'close' )
        super().handle_close()

    def is_my_network( self, peer_ip_str : str ):

        max_bits = 32
        ip_str_to_long = \
            lambda ip_str: struct.unpack( '!L', socket.inet_aton( ip_str ) )[0]
        if ':' in peer_ip_str:
            # IPv6 detected.
            max_bits = 128
            ip_str_to_long = \
                lambda ip_str: struct.unpack( '>QQ',
                    socket.inet_pton( socket.AF_INET6, ip_str ) )[0] << 64 | \
                struct.unpack( '>QQ',
                    socket.inet_pton( socket.AF_INET6, ip_str ) )[1]

        peer_ip_num = ip_str_to_long( peer_ip_str )

        self.logger.debug( 'for ip: %s', peer_ip_str )

        for network in self.mynetworks:

            if 32 == max_bits and ':' in network[0]:
                # Peer address is IPv4 and this network is IPv6.
                continue
            elif 128 == max_bits and ':' not in network[0]:
                # Peer address is IPv6 and this network is IPv4.
                continue

            self.logger.debug( 'testnet : %s', network[0] )

            self.logger.debug( 'peernum : {0:b}'.format( peer_ip_num ) )

            # Get the subnet mask for testing network.
            test_mask = ((2 << int( network[1] ) - 1) - 1)
            fill_bits = (max_bits - int( network[1] ))
            test_mask <<= fill_bits
            self.logger.debug( 'testmask: {0:b}'.format( test_mask ) )

            assert( 0 < test_mask )

            # Get the masked bits for testing network.
            test_ip_num = ip_str_to_long( network[0] )
            test_ip_num &= test_mask
            self.logger.debug( 'testbits: {0:b}'.format( test_ip_num ) )

            peer_net = peer_ip_num & test_mask
            self.logger.debug( 'peernet : {0:b}'.format( peer_net ) )
            if peer_net == test_ip_num:
                self.logger.debug( 'true' )
                return True

        return False

    def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):

        assert( tuple == type( peer ) )
        assert( str == type( peer[0] ) )

        if not self.is_my_network( peer[0] ):
            self.logger.warning( 'rejected unlisted network for peer: %s', peer )
            return '554 Relay access denied'

        self.logger.info( 'connection established by %s', peer )
        msg = email.message_from_string( data.decode( 'utf-8' ) )
        self.logger.info( 'incoming message from %s to %s',
            msg['From'], msg['To'] )

        msg = self.fix_message( peer, msg )

        for module in self.relay_modules:
            try:
                relay = module.RELAY( **self.module_cfgs[module.__loader__.name] )
                relay.send_email( msg )
            except Exception as exc:
                self.logger.error( 'while relaying: %s', exc )
                return '421 The service is unavailable'
