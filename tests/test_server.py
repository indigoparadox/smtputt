
import logging
import unittest
import random
import email
import email.message
import os
import sys
import shutil
import time
import tempfile
from contextlib import contextmanager
from unittest.mock import patch, Mock
from smtplib import SMTP as SMTPClient, SMTPAuthenticationError, SMTPDataError, SMTPResponseException

from faker import Faker

sys.path.append( os.path.dirname( __file__ ) )

from fake_smtp import FakeSMTP
import smtputt.config
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

        self.server_v4 = None
        self.server_v6 = None
        while not self.server_v4 or not self.server_v6:
            self.listen_port = random.randrange( 40000, 50000 )
            server_args['listenport'] = str( self.listen_port )
            try:
                server_args['listenhost'] = '127.0.0.1'
                self.server_v4 =  smtputt.server.SMTPuttServer(
                    module_cfgs, **server_args )
                server_args['listenhost'] = '::1'
                self.server_v6 =  smtputt.server.SMTPuttServer(
                    module_cfgs, **server_args )
            except OSError:
                # Port in use.
                pass

        self.mock_relay_module = Mock()
        self.mock_relay_module.__loader__ = Mock()
        self.mock_relay_module.__loader__.name = Mock()
        self.mock_relay_module.__loader__.name = 'mock_relay'
        self.mock_relay_module.RELAY.return_value = self.relay
        self.server_v4.relay_modules = [self.mock_relay_module]
        self.server_v6.relay_modules = [self.mock_relay_module]

        self.server_v4.serve_thread( daemonize=True )
        self.server_v6.serve_thread( daemonize=True )

        logging.getLogger( 'channel' ).setLevel( logging.DEBUG )

    def tearDown( self ):
        self.server_v4.close()
        self.server_v6.close()

    @contextmanager
    def create_mock_server( self, listen_host ):
        listen_server = self.server_v4
        if '::1' == listen_host:
            listen_server = self.server_v6
        with patch( 'smtputt.server.SMTPuttServer', autospec=True ) as mock_server:
            mock_server.channels = Mock()
            mock_server.channels.remove = Mock( side_effect=
                lambda c: listen_server.channels.remove( c ) )
            mock_server.process_message = Mock( side_effect=
                lambda peer, mailfrom, rcpttos, data, **kwargs:
                    listen_server.process_message(
                        peer, mailfrom, rcpttos, data, **kwargs ) )
            yield mock_server

    def test_create_config( self ):
        logging.getLogger( 'config' ).setLevel( logging.DEBUG )
        temp_dir_path = tempfile.mkdtemp()
        smtputt.config.sys = Mock()

        config_paths = [
            os.path.join( temp_dir_path, 'smtputt.ini' )
        ]

        try:
            smtputt.config.load_or_create_config( True, config_paths )
            smtputt.config.sys.exit.assert_called_with( 1 )
            self.assertTrue( os.path.exists( config_paths[0] ) )
        finally:
            shutil.rmtree( temp_dir_path )

    def test_auth( self ):

        # TODO: IPv6 test_auth.
        with SMTPClient( '127.0.0.1', self.listen_port ) as smtp:
            self.assertEqual(
                self.server_v4.channels[0]._auth_login_stage,
                SMTPuttAuthStatus.AUTH_NONE )
            smtp.login( 'testuser1', 'testpass1' )
            self.assertEqual(
                self.server_v4.channels[0]._auth_login_stage,
                SMTPuttAuthStatus.AUTH_SUCCESSFUL )

    def test_auth_fail( self ):

        # TODO: IPv6 test_auth_fail.
        try:
            with SMTPClient( '127.0.0.1', self.listen_port ) as smtp:
                self.assertEqual(
                    self.server_v4.channels[0]._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )
                with self.assertRaises( SMTPAuthenticationError ):
                    smtp.login( 'testuser1', 'testpass2' )
                self.assertEqual(
                    self.server_v4.channels[0]._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )
        except SMTPResponseException:
            pass

    def test_failauth_message( self ):

        msg = self.fake.email_msg()

        # TODO: IPv6 test_failauth_message.
        with self.assertRaises( SMTPResponseException ):
            with SMTPClient( '127.0.0.1', self.listen_port ) as smtp:
                attempt = 0
                while 0 >= len( self.server_v4.channels ) and attempt < 5:
                    time.sleep( 1 )
                    attempt += 1
                channel = self.server_v4.channels[0]
                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )

                with self.assertRaises( SMTPAuthenticationError ):
                    smtp.login( 'testuser1', 'testpass2' )

                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )

                # Replace the channel's server for testing.
                with self.create_mock_server( '127.0.0.1' ) as mock_server:
                    channel.smtp_server = mock_server
                    smtp.sendmail( msg['From'], msg['To'], msg.as_string() )
                    mock_server.process_message.assert_not_called()

        self.assertIsNone( self.relay.last_msg )

    def test_unauth_message( self ):

        msg = self.fake.email_msg()

        # TODO: IPv6 test_unauth_message.
        with self.assertRaises( SMTPResponseException ):
            with SMTPClient( '127.0.0.1', self.listen_port ) as smtp:
                attempt = 0
                while 0 >= len( self.server_v4.channels ) and attempt < 5:
                    time.sleep( 1 )
                    attempt += 1
                channel = self.server_v4.channels[0]
                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )

                # Replace the channel's server for testing.
                with self.create_mock_server( '127.0.0.1' ) as mock_server:
                    channel.smtp_server = mock_server
                    smtp.sendmail( msg['From'], msg['To'], msg.as_string() )
                    mock_server.process_message.assert_not_called()

        self.assertIsNone( self.relay.last_msg )

    def test_process_message( self ):

        for local_ip in '::1', '127.0.0.1':

            listen_server = self.server_v6 if '::1' == local_ip \
                else self.server_v4

            msg = self.fake.email_msg()

            msg_from = msg['From']
            msg_to = msg['To']

            with SMTPClient( local_ip, self.listen_port ) as smtp:
                channel = listen_server.channels[0]
                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_NONE )
                smtp.login( 'testuser1', 'testpass1' )
                self.assertEqual(
                    channel._auth_login_stage,
                    SMTPuttAuthStatus.AUTH_SUCCESSFUL )

                # Replace the channel's server for testing.
                with self.create_mock_server( local_ip ) as mock_server:
                    channel.smtp_server = mock_server
                    smtp.sendmail( msg['From'], msg['To'], msg.as_string() )
                    mock_server.process_message.assert_called_once()

            self.assertIsNotNone( self.relay.last_msg )
            self.assertEqual( self.relay.last_msg['To'], msg_to )
            self.assertEqual( self.relay.last_msg['From'], msg_from )

    def test_relay_crash( self ):
        self.relay.send_email = Mock( side_effect=ConnectionError )

        msg = self.fake.email_msg()

        # TODO: IPv6 test_relay_crash.
        with SMTPClient( '127.0.0.1', self.listen_port ) as smtp:
            attempt = 0
            while 0 >= len( self.server_v4.channels ) and attempt < 5:
                time.sleep( 1 )
                attempt += 1
            channel = self.server_v4.channels[0]
            self.assertEqual(
                channel._auth_login_stage,
                SMTPuttAuthStatus.AUTH_NONE )
            smtp.login( 'testuser1', 'testpass1' )
            self.assertEqual(
                channel._auth_login_stage,
                SMTPuttAuthStatus.AUTH_SUCCESSFUL )

            # Replace the channel's server for testing.
            with self.create_mock_server( '127.0.0.1' ) as mock_server:
                channel.smtp_server = mock_server
                with self.assertRaises( SMTPDataError ) as exc:
                    smtp.sendmail( msg['From'], msg['To'], msg.as_string() )
                    self.assertEqual( 421, exc.exception.smtp_code )

    def test_auth_crash( self ):

        msg = self.fake.email_msg()

        # TODO: IPv6 test_auth_crash.
        with SMTPClient( '127.0.0.1', self.listen_port ) as smtp:
            attempt = 0
            while 0 >= len( self.server_v4.channels ) and attempt < 5:
                time.sleep( 1 )
                attempt += 1
            channel = self.server_v4.channels[0]
            channel.auth_classes[0].authorize = \
                Mock( side_effect=ConnectionError( 'this is expected' ) )
            with self.assertRaises( SMTPAuthenticationError ) as exc:
                smtp.login( 'testuser1', 'testpass1' )

                self.assertEqual( 454, exc.exception.smtp_code )

            # Should have failed by here.

    def test_is_my_network( self ):

        self.server_v4.mynetworks = [
            ('127.0.0.0', '8'),
            ('192.168.10.0', '24'),
            ('10.10.0.0', '16'),
            ('::1', '128'),
            ('2001:db8:3333:5555::', '56')
        ]

        self.server_v6.mynetworks = [
            ('127.0.0.0', '8'),
            ('192.168.10.0', '24'),
            ('10.10.0.0', '16'),
            ('::1', '128'),
            ('2001:db8:3333:5555::', '56')
        ]

        #self.server_v4.logger.setLevel( logging.DEBUG )
        #self.server_v4.logger.addHandler( logging.StreamHandler( sys.stdout ) )
        #self.server_v6.logger.setLevel( logging.DEBUG )
        #self.server_v6.logger.addHandler( logging.StreamHandler( sys.stdout ) )

        self.assertTrue( self.server_v4.is_my_network( '192.168.10.5' ) )
        self.assertFalse( self.server_v4.is_my_network( '192.168.18.5' ) )
        self.assertTrue( self.server_v4.is_my_network( '10.10.12.14' ) )
        self.assertFalse( self.server_v4.is_my_network( '65.83.128.3' ) )

        self.assertTrue( self.server_v6.is_my_network( '::1' ) )
        self.assertFalse( self.server_v6.is_my_network( '2001:db8:3333:4444:5555:6666:7777:8888' ) )
        self.assertTrue( self.server_v6.is_my_network( '2001:db8:3333:5555:4444:6666:7777:8888' ) )
