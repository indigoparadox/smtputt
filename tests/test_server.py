
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
from smtp_helper import create_server, create_test_server
from smtputt.server import SMTPuttServer

class TestServer( unittest.TestCase ):

    def setUp( self ):
        self.fake = Faker()
        self.fake.add_provider( FakeSMTP )

        self.server_args = {
            'listenhost': 'localhost',
            'listenport': None,
            'remoteserver': 'localhost',
            'remotessl': 'false',
            'authmodule': 'smtputt.authorization.dictauth',
            'authrequired': 'true',
            'authdict': 'testuser1:testpass1,testuser2:testpass2'
        }

        logging.getLogger( 'channel' ).setLevel( logging.DEBUG )

    def test_auth( self ):

        msg = self.fake.email_msg()

        msg_from = msg['From']
        msg_to = msg['To']

        server_args = self.server_args.copy()
        with create_test_server() as test_server:
            with create_server(
            test_server.smtp_listen, server_args ):
                with SMTPClient(
                'localhost', int( server_args['listenport'] ) ) as smtp:
                    smtp.login( 'testuser1', 'testpass1' )
                    smtp.sendmail(
                        msg['From'], msg['To'], msg.as_string() )

            self.assertIsNotNone( test_server.last_msg )
            self.assertEqual( test_server.last_msg['To'], msg_to )
            self.assertEqual( test_server.last_msg['From'], msg_from )

    def test_auth_fail( self ):

        server_args = self.server_args.copy()
        with create_test_server() as test_server:
            with create_server(
            test_server.smtp_listen, server_args ):
                with SMTPClient(
                'localhost', int( server_args['listenport'] ) ) as smtp:
                    with self.assertRaises( SMTPAuthenticationError ):
                        smtp.login( 'testuser1', 'testpass2' )

    def test_process_message( self ):

        server_args_noauth = self.server_args.copy()
        del server_args_noauth['authrequired']
        del server_args_noauth['authmodule']

        msg = self.fake.email_msg()

        msg_from = msg['From']
        msg_to = msg['To']

        with create_test_server() as test_server:
            with create_server(
            test_server.smtp_listen, server_args_noauth ):
                with SMTPClient(
                'localhost',
                int( server_args_noauth['listenport'] ) ) as smtp:
                    smtp.sendmail(
                        msg['From'], msg['To'], msg.as_string() )

            self.assertIsNotNone( test_server.last_msg )
            self.assertEqual( test_server.last_msg['To'], msg_to )
            self.assertEqual( test_server.last_msg['From'], msg_from )
