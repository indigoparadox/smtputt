
from ssl import SSLError
import unittest
import email
import os
import sys
import email.message
from smtplib import SMTP_SSL

sys.path.append( os.path.dirname( __file__ ) )

from smtp_helper import TestSMTPServer
from smtputt.relay import SMTPuttRelay

class TestRelay( unittest.TestCase ):

    def setUp(self) -> None:

        self.smtp_listen : int
        self.smtp = None
        while not self.smtp:
            # If random ports collide, retry.
            try:
                self.smtp = TestSMTPServer( self )
            except OSError:
                self.smtp = None
        relay_args = {
            'remoteserver': 'localhost',
            'remoteport': self.smtp_listen,
            'remotessl': 'false'
        }
        self.last_msg : email.message.EmailMessage
        self.relay = SMTPuttRelay( **relay_args )

    def tearDown(self) -> None:
        self.smtp.close()

    def test_send_email( self ):

        msg = email.message.EmailMessage()
        msg.add_header( 'To', 'test@example.com' )
        msg.add_header( 'From', 'smtputt@example.com' )
        msg.set_content( '\r\n' )

        self.relay.send_email( msg )

        self.assertIsNotNone( self.last_msg )
        self.assertEqual( self.last_msg['To'], 'test@example.com' )
        self.assertEqual( self.last_msg['From'], 'smtputt@example.com' )

    def test_send_email_ssl( self ):

        self.relay.smtp_class = SMTP_SSL

        msg = email.message.EmailMessage()
        msg.add_header( 'To', 'test@example.com' )
        msg.add_header( 'From', 'smtputt@example.com' )

        with self.assertRaises( SSLError ):
            self.relay.send_email( msg )
