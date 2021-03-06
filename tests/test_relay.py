
from ssl import SSLError
import unittest
import email
import os
import sys
import email.message
from unittest.mock import Mock, patch

sys.path.append( os.path.dirname( __file__ ) )

import smtputt.relay

class TestRelay( unittest.TestCase ):

    def setUp(self) -> None:
        self.relay_args = {
            'remoteserver': 'localhost',
            'remoteport': 25,
            'remotessl': 'false'
        }

    def test_send_email( self ):

        msg = email.message.EmailMessage()
        msg.add_header( 'To', 'test@example.com' )
        msg.add_header( 'From', 'smtputt@example.com' )
        msg.set_content( '\r\n' )

        relay_args = self.relay_args.copy()

        with patch( 'smtplib.SMTP', autospec=True ) as mock_smtp:
            smtputt.relay.SMTP = mock_smtp
            relay = smtputt.relay.SMTPuttRelay( **relay_args )
            relay.send_email( msg )
            mock_smtp.assert_called_with( 'localhost', 25 )
            mock_instance = mock_smtp.return_value.__enter__.return_value
            mock_instance.sendmail.assert_called_with( msg['From'], msg['To'], msg.as_string() )

    def test_send_email_ssl( self ):

        msg = email.message.EmailMessage()
        msg.add_header( 'To', 'test@example.com' )
        msg.add_header( 'From', 'smtputt@example.com' )

        relay_args = self.relay_args.copy()
        relay_args['remotessl'] = 'true'

        with patch( 'smtplib.SMTP_SSL', autospec=True ) as mock_smtp:
            smtputt.relay.SMTP_SSL = mock_smtp
            relay = smtputt.relay.SMTPuttRelay( **relay_args )
            relay.send_email( msg )
            mock_smtp.assert_called_with( 'localhost', 25 )
            mock_instance = mock_smtp.return_value.__enter__.return_value
            mock_instance.sendmail.assert_called_with( msg['From'], msg['To'], msg.as_string() )
