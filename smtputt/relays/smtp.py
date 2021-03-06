
import logging
from smtplib import SMTP, SMTPException, SMTP_SSL

from . import SMTPuttRelay

class SMTPuttSMTPRelay( SMTPuttRelay ):

    def __init__( self, **kwargs ):

        super().__init__( **kwargs )

        self.logger = logging.getLogger( 'relay' )
        self.out_server = kwargs['remoteserver']
        self.out_port = int( kwargs['remoteport'] ) if 'remoteport' in kwargs \
            else 25
        self.out_user = kwargs['remoteuser'] if 'remoteuser' in kwargs \
            else None
        self.out_password = kwargs['remotepassword'] if 'remotepassword' \
            in kwargs else None
        self.smtp_class = SMTP if 'remotessl' in kwargs \
            and 'false' == kwargs['remotessl'] else SMTP_SSL

    def send_email( self, msg ):
        try:
            with self.smtp_class( self.out_server, self.out_port ) as smtp:
                if self.out_user or self.out_password:
                    smtp.login( self.out_user, self.out_password )
                res = smtp.sendmail(
                    msg['From'], msg['To'], msg.as_string() )
                self.logger.info( 'message forwarded without error.' )
        except SMTPException as exc:
            # TODO: Store message and try every so often until success.
            self.logger.error( 'error while forwarding message: %s', exc )
