
import logging
from smtplib import SMTP, SMTPConnectError, SMTPDataError, SMTPException, SMTP_SSL

class SMTPuttRelay( object ):

    def __init__( self, **kwargs ):

        self.logger = logging.getLogger( 'relay' )

        self.domains = kwargs['relaydomains'] if 'relaydomains' in kwargs \
            else ['*']

    def check_domain( self, address ):
        # TODO
        pass

    def send_email( self, msg ):
        pass
