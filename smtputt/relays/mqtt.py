
import logging

from paho.mqtt import client as mqtt_client

class SMTPuttRelay( object ):

    def __init__( self, **kwargs ):

        self.logger = logging.getLogger( 'relay' )

    def send_email( self, msg ):
        pass
