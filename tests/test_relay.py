
import unittest
import os
import sys
import email
import email.message
from unittest.mock import patch, Mock

from faker import Faker

sys.path.append( os.path.dirname( __file__ ) )

from fake_smtp import FakeSMTP
import smtputt.relays.smtp
import smtputt.relays.mqtt

class TestRelay( unittest.TestCase ):

    def setUp( self ):
        self.fake = Faker()
        self.fake.add_provider( FakeSMTP )

    def test_send_email( self ):

        msg = email.message.EmailMessage()
        msg.add_header( 'To', 'test@example.com' )
        msg.add_header( 'From', 'smtputt@example.com' )
        msg.set_content( '\r\n' )

        relay_args = {
            'remoteserver': 'localhost',
            'remoteport': 25,
            'remotessl': 'false'
        }

        with patch( 'smtplib.SMTP', autospec=True ) as mock_smtp:
            smtputt.relays.smtp.SMTP = mock_smtp
            relay = smtputt.relays.smtp.SMTPuttSMTPRelay( **relay_args )
            relay.send_email( msg )
            mock_smtp.assert_called_with( 'localhost', 25 )
            mock_instance = mock_smtp.return_value.__enter__.return_value
            mock_instance.sendmail.assert_called_with(
                msg['From'], msg['To'], msg.as_string() )

    def test_send_email_ssl( self ):

        msg = email.message.EmailMessage()
        msg.add_header( 'To', 'test@example.com' )
        msg.add_header( 'From', 'smtputt@example.com' )

        relay_args = {
            'remoteserver': 'localhost',
            'remoteport': 25,
            'remotessl': 'true'
        }

        with patch( 'smtplib.SMTP_SSL', autospec=True ) as mock_smtp:
            smtputt.relays.smtp.SMTP_SSL = mock_smtp
            relay = smtputt.relays.smtp.SMTPuttSMTPRelay( **relay_args )
            relay.send_email( msg )
            mock_smtp.assert_called_with( 'localhost', 25 )
            mock_instance = mock_smtp.return_value.__enter__.return_value
            mock_instance.sendmail.assert_called_with(
                msg['From'], msg['To'], msg.as_string() )

    def test_send_email_mqtt( self ):

        msg = self.fake.email_msg()

        relay_args = {
            'mqttserver': 'localhost',
            'mqttport': 1883,
            'mqttuid': 'testuid',
            'mqtttopic': 'testtopic/%t'
        }

        with patch( 'paho.mqtt.client', autospec=True ) as mock_mqtt:
            smtputt.relays.mqtt.mqtt_client = mock_mqtt
            mock_instance = mock_mqtt.Client.return_value
            mock_instance.is_connected.return_value = True

            relay = smtputt.relays.mqtt.SMTPuttMQTTRelay( **relay_args )
            relay.send_email( msg )

            mock_instance.is_connected.assert_called_once_with()
            mock_instance.publish.assert_called_once_with(
                relay_args['mqtttopic'].replace( '%t', msg['To'] ),
                msg.as_string()
            )
            #mock_mqtt.assert_called_with( 'localhost', 25 )
            #mock_instance = mock_mqtt.return_value.__enter__.return_value
            #mock_instance.sendmail.assert_called_with(
            #    msg['From'], msg['To'], msg.as_string() )
