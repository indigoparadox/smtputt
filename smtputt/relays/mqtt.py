
from email.message import EmailMessage
import logging
import ssl
import json
import email

from paho.mqtt import client as mqtt_client

from . import SMTPuttRelay

class SMTPuttMQTTRelay( SMTPuttRelay ):

    def __init__( self, **kwargs ):

        self.logger = logging.getLogger( 'relay' )

        self.publish_on_connect : str
        self.publish_on_connect = None
        self.topic = kwargs['mqtttopic']
        self.mqtt = mqtt_client.Client(
            kwargs['mqttuid'], True, None, mqtt_client.MQTTv31 )
        self.mqtt.loop_start()
        if 'mqttlogger' in kwargs and kwargs['mqttlogger'] == 'true':
            self.mqtt.enable_logger()
        if 'mqttssl' in kwargs and kwargs['mqttssl'] == 'true':
            self.mqtt.tls_set(
                kwargs['mqttca'], tls_version=ssl.PROTOCOL_TLSv1_2 )
        self.mqtt.on_connect = self.on_connected
        self.logger.info( 'connecting to MQTT at %s:%d...',
            kwargs['mqttserver'], int( kwargs['mqttport'] ) )
        self.mqtt.connect( kwargs['mqttserver'], int( kwargs['mqttport'] ) )

    def send_email( self, msg ):
        if self.mqtt.is_connected():
            self.publish_msg( msg )
        else:
            self.publish_on_connect = msg

    def publish_msg( self, msg : EmailMessage ):
        #msg_json = json.dumps( msg.as_string() )
        topic = self.topic.replace( '%t', msg['To'] )
        topic = topic.replace( '%f', msg['From'] )
        topic = topic.replace( '%s', msg['Subject'] if 'Subject' in msg else '' )
        self.mqtt.publish( topic, msg.as_string() )
        self.stop()

    def on_connected( self, client,  userdata, flags, rc ):
        self.logger.info( 'mqtt connected' )
        if self.publish_on_connect:
            self.publish_msg( self.publish_on_connect )

    def stop( self ):
        self.logger.info( 'mqtt shutting down...' )
        self.mqtt.disconnect()
        self.mqtt.loop_stop()

RELAY = SMTPuttMQTTRelay
