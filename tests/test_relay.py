
from ssl import SSLError
import unittest
import email
import email.message
import asyncore
import random
from smtpd import SMTPServer
from smtplib import SMTP_SSL
from threading import Thread

from smtputt.relay import SMTPuttRelay

class TestRelay( unittest.TestCase ):

    class TestSMTPServer( SMTPServer ):

        def __init__( self, tester ):
            listen_port = random.randrange( 40000, 50000 )
            super().__init__( ('localhost', listen_port), None )
            self.tester = tester
            self.tester.smtp_listen = listen_port
            self.thread = Thread( target=asyncore.loop, daemon=True )
            self.thread.start()

        def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):
            self.tester.last_msg = email.message_from_bytes( data )

    def setUp(self) -> None:

        self.smtp_listen : int
        self.smtp = None
        while not self.smtp:
            # If random ports collide, retry.
            try:
                self.smtp = self.TestSMTPServer( self )
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
