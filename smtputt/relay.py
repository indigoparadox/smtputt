
import logging
from smtplib import SMTP, SMTP_SSL

class SMTPuttRelay( object ):

    def __init__( self, **kwargs ):

        self.logger = logging.getLogger( 'relay' )
        self.out_server = kwargs['remoteserver']
        self.out_port = int( kwargs['remoteport'] ) if 'remoteport' in kwargs \
            else 25
        self.out_user = kwargs['remoteuser'] if 'remoteuser' in kwargs \
            else None
        self.out_password = kwargs['remotepassword'] if 'remotepassword' \
            in kwargs else None

    def send_mail( self, msg ):
        with SMTP_SSL( self.out_server, self.out_port ) as smtp:
            smtp.login( self.out_user, self.out_password )
            try:
                res = smtp.sendmail( 
                    self.from_addr, msg['To'], msg.as_string() )
                self.logger.info( 'message forwarded without error.' )
            except Exception as exc:
                self.logger.error( 'error while forwarding message: %s', exc )
