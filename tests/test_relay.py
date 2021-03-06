
from ssl import SSLError
import unittest
import email
import os
import sys
import email.message
from smtplib import SMTP_SSL

sys.path.append( os.path.dirname( __file__ ) )

from smtp_helper import create_test_server
from smtputt.relay import SMTPuttRelay

class TestRelay( unittest.TestCase ):

    def setUp(self) -> None:
        self.relay_args = {
            'remoteserver': 'localhost',
            'remoteport': None,
            'remotessl': 'false'
        }

    def test_send_email( self ):

        with create_test_server() as remote_server:

            msg = email.message.EmailMessage()
            msg.add_header( 'To', 'test@example.com' )
            msg.add_header( 'From', 'smtputt@example.com' )
            msg.set_content( '\r\n' )

            relay_args = self.relay_args.copy()
            relay_args['remoteport'] = str( remote_server.smtp_listen )

            relay = SMTPuttRelay( **relay_args )
            relay.send_email( msg )

            self.assertIsNotNone( remote_server.last_msg )
            self.assertEqual( remote_server.last_msg['To'], 'test@example.com' )
            self.assertEqual( remote_server.last_msg['From'], 'smtputt@example.com' )

    def test_send_email_ssl( self ):

        with create_test_server() as remote_server:

            msg = email.message.EmailMessage()
            msg.add_header( 'To', 'test@example.com' )
            msg.add_header( 'From', 'smtputt@example.com' )

            relay_args = self.relay_args.copy()
            relay_args['remoteport'] = str( remote_server.smtp_listen )
            relay_args['remotessl'] = True
            relay = SMTPuttRelay( **relay_args )

            with self.assertRaises( SSLError ):
                relay.send_email( msg )
