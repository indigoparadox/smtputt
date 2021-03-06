
import logging
import unittest
import random
import email
import email.message
import os
import sys
import time
from contextlib import contextmanager
from smtplib import SMTP as SMTPClient, SMTPAuthenticationError

from faker import Faker

sys.path.append( os.path.dirname( __file__ ) )

from fake_smtp import FakeSMTP
from smtputt.server import SMTPuttServer

class TestServer( unittest.TestCase ):

    class FakeRelay( object ):

        def __init__( self ):
            self.last_msg : email.message.EmailMessage
            self.last_msg = None

        def send_email( self, msg ):
            self.last_msg = msg

    def setUp( self ):
        self.fake = Faker()
        self.fake.add_provider( FakeSMTP )

        self.server_args = {
            'listenhost': 'localhost',
            'listenport': None,
            'authmodule': 'smtputt.authorization.dictauth',
            'authrequired': 'true',
            'authdict': 'testuser1:testpass1,testuser2:testpass2'
        }

        logging.getLogger( 'channel' ).setLevel( logging.DEBUG )

    @contextmanager
    def create_server( self, server_args ):
        server = None
        while not server:
            server_args['listenport'] = str( random.randrange( 40000, 50000 ) )
            try:
                server = SMTPuttServer( **server_args )
            except OSError:
                # Port in use.
                pass
        server.serve_thread( daemonize=True )
        try:
            yield server
        finally:
            server.close()

    def test_auth( self ):

        msg = self.fake.email_msg()

        msg_from = msg['From']
        msg_to = msg['To']

        relay = self.FakeRelay()
        server_args = self.server_args.copy()
        server_args['relay'] = relay
        with self.create_server( server_args ):
            with SMTPClient(
            'localhost', int( server_args['listenport'] ) ) as smtp:
                smtp.login( 'testuser1', 'testpass1' )
                smtp.sendmail( msg['From'], msg['To'], msg.as_string() )

        self.assertIsNotNone( relay.last_msg )
        self.assertEqual( relay.last_msg['To'], msg_to )
        self.assertEqual( relay.last_msg['From'], msg_from )

    def test_auth_fail( self ):

        relay = self.FakeRelay()
        server_args = self.server_args.copy()
        server_args['relay'] = relay
        with self.create_server( server_args ):
            with SMTPClient(
            'localhost', int( server_args['listenport'] ) ) as smtp:
                with self.assertRaises( SMTPAuthenticationError ):
                    smtp.login( 'testuser1', 'testpass2' )

    def test_process_message( self ):

        relay = self.FakeRelay()
        server_args_noauth = self.server_args.copy()
        server_args_noauth['relay'] = relay
        del server_args_noauth['authrequired']
        del server_args_noauth['authmodule']

        msg = self.fake.email_msg()

        msg_from = msg['From']
        msg_to = msg['To']

        with self.create_server( server_args_noauth ):
            with SMTPClient(
            'localhost',
            int( server_args_noauth['listenport'] ) ) as smtp:
                smtp.sendmail( msg['From'], msg['To'], msg.as_string() )

        self.assertIsNotNone( relay.last_msg )
        self.assertEqual( relay.last_msg['To'], msg_to )
        self.assertEqual( relay.last_msg['From'], msg_from )
