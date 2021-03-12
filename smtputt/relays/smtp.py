
import ssl
import logging
from smtplib import SMTP, SMTPException, SMTP_SSL
from urllib.parse import urlparse

from . import SMTPuttRelay

class SMTPuttSMTPRelay( SMTPuttRelay ):

    def __init__( self, **kwargs ):

        super().__init__( **kwargs )

        smtp_url = urlparse( kwargs['smtpurl'] )

        self.logger = logging.getLogger( 'relay' )
        self.out_server = smtp_url.hostname
        self.out_port = smtp_url.port if smtp_url.port else 25
        self.out_user = smtp_url.username
        self.out_password = smtp_url.password
        #self.smtp_class = SMTP_SSL if 'smtps' == smtp_url.scheme else SMTP
        self.ssl = ('smtps' == smtp_url.scheme)

    def send_email( self, msg ):
        try:
            with SMTP( self.out_server, self.out_port ) as smtp:
                smtp.ehlo()
                if self.ssl:
                    context = ssl.SSLContext( ssl.PROTOCOL_TLS )
                    smtp.starttls( context=context )
                    smtp.ehlo()
                if self.out_user or self.out_password:
                    smtp.login( self.out_user, self.out_password )
                res = smtp.sendmail(
                    msg['From'], msg['To'], msg.as_string() )
                self.logger.info( 'message forwarded without error.' )
        except SMTPException as exc:
            # TODO: Store message and try every so often until success.
            self.logger.error( 'error while forwarding message: %s', exc )

RELAY = SMTPuttSMTPRelay
