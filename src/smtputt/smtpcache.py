
from smtpd import SMTPServer
from smtplib import SMTP_SSL
from email.utils import formatdate
import email
import logging

class SMTPCache( SMTPServer ):

    def __init__( self, listen_addr, out_server, out_port, out_user, out_password, from_addr ):
        self.out_server = out_server
        self.out_port = out_port
        self.out_user = out_user
        self.out_password = out_password
        self.from_addr = from_addr
        super().__init__( listen_addr, None )

    def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):

        logger = logging.getLogger( 'smtpcache.process' )

        logger.info( 'connection established...' )

        msg = email.message_from_string( data.decode( 'utf-8' ) )

        msg.replace_header( 'From', self.from_addr )
        msg.add_header( 'Date', formatdate() )

        logger.info( 'incoming message from {} to {}'.format( msg['From'], msg['To'] ) )

        with SMTP_SSL( self.out_server, self.out_port ) as smtp:
            smtp.login( self.out_user, self.out_password )
            try:
                res = smtp.sendmail( 'noreply@centralvetalbany.com', msg['To'], msg.as_string() )
                logger.info( 'message forwarded without error.' )
            except Exception as e:
                logger.error( e )

