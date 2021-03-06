
import logging
import unittest
import random
import email
import email.message
import os
import sys
from contextlib import contextmanager
from unittest.mock import patch, Mock
from smtplib import SMTP as SMTPClient, SMTPAuthenticationError, SMTPResponseException

from faker import Faker

sys.path.append( os.path.dirname( __file__ ) )

from fake_smtp import FakeSMTP
import smtputt.server
from smtputt.channel import SMTPuttAuthStatus

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
            'authmodules': 'smtputt.authorization.dictauth',
            'authrequired': 'true',
            'relay': self.relay
        }

        module_cfgs = {
            'smtputt.authorization.dictauth': {
                'authdict': 'testuser1:testpass1,testuser2:testpass2'
            },
            'mock_relay': {

            }
        }

        self.server = None
        while not self.server:
            self.listen_port = random.randrange( 40000, 50000 )
            server_args['listenport'] = str( self.listen_port )
            try:
                self.server =  smtputt.server.SMTPuttServer( module_cfgs, **server_args )
            except OSError:
                # Port in use.
                pass

        self.mock_relay_module = Mock()
        self.mock_relay_module.__loader__ = Mock()
        self.mock_relay_module.__loader__.name = Mock()
        self.mock_relay_module.__loader__.name = 'mock_relay'
        self.mock_relay_module.RELAY.return_value = self.relay
        self.server.relay_modules = [self.mock_relay_module]

        self.server.serve_thread( daemonize=True )

        logging.getLogger( 'channel' ).setLevel( logging.DEBUG )

    def tearDown( self ):
        self.server.close()

    @contextmanager
    def create_mock_server( self ):
        with patch( 'smtputt.server.SMTPuttServer', autospec=True ) as mock_server:
            mock_server.channels = Mock()
            mock_server.channels.remove = Mock( side_effect=
                lambda c: self.server.channels.remove( c ) )
            mock_server.process_message = Mock( side_effect=
                lambda peer, mailfrom, rcpttos, data, **kwargs:
                    self.server.process_message(
                        peer, mailfrom, rcpttos, data, **kwargs ) )
            yield mock_server

    def test_auth( self ):

        with SMTPClient( 'localhost', self.listen_port ) as smtp:
            self.assertEqual(
                self.server.channels[0]._auth_login_stage,
                SMTPuttAuthStatus.AUTH_NONE )
            smtp.login( 'testuser1', 'testpass1' )
            self.assertEqual(
                self.server.channels[0]._auth_login_stage,
                SMTPuttAuthStatus.AUTH_SUCCESSFUL )

    def test_auth_fail( self ):

        with SMTPClient( 'localhost', self.listen_port ) as smtp:
            self.assertEqual(
                self.server.channels[0]._auth_login_stage,
                SMTPuttAuthStatus.AUTH_NONE )
            with self.assertRaises( SMTPAuthenticationError ):
                smtp.login( 'testuser1', 'testpass2' )
            self.assertEqual(
                self.server.channels[0]._auth_login_stage,
                SMTPuttAuthStatus.AUTH_NONE )

    def test_failauth_message( self ):

        msg = self.fake.email_msg()

        with self.assertRaises( SMTPResponseException ):
            with SMTPClient( 'localhost', self.listen_port ) as smtp:
                channel = self.server.channels[0]
                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )

                with self.assertRaises( SMTPAuthenticationError ):
                    smtp.login( 'testuser1', 'testpass2' )

                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )

                # Replace the channel's server for testing.
                with self.create_mock_server() as mock_server:
                    channel.smtp_server = mock_server
                    smtp.sendmail( msg['From'], msg['To'], msg.as_string() )
                    mock_server.process_message.assert_not_called()

        self.assertIsNone( self.relay.last_msg )

    def test_unauth_message( self ):

        msg = self.fake.email_msg()

        with self.assertRaises( SMTPResponseException ):
            with SMTPClient( 'localhost', self.listen_port ) as smtp:
                channel = self.server.channels[0]
                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )

                # Replace the channel's server for testing.
                with self.create_mock_server() as mock_server:
                    channel.smtp_server = mock_server
                    smtp.sendmail( msg['From'], msg['To'], msg.as_string() )
                    mock_server.process_message.assert_not_called()

        self.assertIsNone( self.relay.last_msg )

    def test_process_message( self ):

        msg = self.fake.email_msg()

        msg_from = msg['From']
        msg_to = msg['To']

        with SMTPClient( 'localhost', self.listen_port ) as smtp:
            channel = self.server.channels[0]
            self.assertEqual(
                channel._auth_login_stage,
                SMTPuttAuthStatus.AUTH_NONE )
            smtp.login( 'testuser1', 'testpass1' )
            self.assertEqual(
                channel._auth_login_stage,
                SMTPuttAuthStatus.AUTH_SUCCESSFUL )

            # Replace the channel's server for testing.
            with self.create_mock_server() as mock_server:
                channel.smtp_server = mock_server
                smtp.sendmail( msg['From'], msg['To'], msg.as_string() )
                mock_server.process_message.assert_called_once()

        self.assertIsNotNone( self.relay.last_msg )
        self.assertEqual( self.relay.last_msg['To'], msg_to )
        self.assertEqual( self.relay.last_msg['From'], msg_from )
