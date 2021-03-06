
from importlib import import_module
import logging
import unittest
import random
import email
import email.message
import os
import sys
from contextlib import contextmanager
from importlib import import_module
from smtplib import SMTP as SMTPClient, SMTPAuthenticationError

from faker import Faker

sys.path.append( os.path.dirname( __file__ ) )

import smtputt.server
from fake_smtp import FakeSMTP

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
        self.relay = self.FakeRelay()

        server_args = {
            'listenhost': 'localhost',
            'listenport': None,
            'authmodule': import_module( 'smtputt.authorization.dictauth' ),
            'authrequired': 'true',
            'authdict': 'testuser1:testpass1,testuser2:testpass2',
            'relay': self.relay
        }

        self.server = None
        while not self.server:
            self.listen_port = random.randrange( 40000, 50000 )
            server_args['listenport'] = str( self.listen_port )
            try:
                self.server =  smtputt.server.SMTPuttServer( **server_args )
            except OSError:
                # Port in use.
                pass
        self.server.serve_thread( daemonize=True )

        logging.getLogger( 'channel' ).setLevel( logging.DEBUG )

    def tearDown( self ):
        self.server.close()

    def test_auth( self ):

        with SMTPClient( 'localhost', self.listen_port ) as smtp:
            smtp.login( 'testuser1', 'testpass1' )

    def test_auth_fail( self ):

        with SMTPClient( 'localhost', self.listen_port ) as smtp:
            with self.assertRaises( SMTPAuthenticationError ):
                smtp.login( 'testuser1', 'testpass2' )

    def test_process_message( self ):

        msg = self.fake.email_msg()

        msg_from = msg['From']
        msg_to = msg['To']

        with SMTPClient( 'localhost', self.listen_port ) as smtp:
            smtp.login( 'testuser1', 'testpass1' )
            smtp.sendmail( msg['From'], msg['To'], msg.as_string() )

        self.assertIsNotNone( self.relay.last_msg )
        self.assertEqual( self.relay.last_msg['To'], msg_to )
        self.assertEqual( self.relay.last_msg['From'], msg_from )
