
from smtpd import SMTPServer
from smtplib import SMTP_SSL
import email
import logging

class SMTPCache( SMTPServer ):

    def __init__( self, listen_addr, out_server, out_port, out_user, out_password ):
        self.out_server = out_server
        self.out_port = out_port
        self.out_user = out_user
        self.out_password = out_password
        super().__init__( listen_addr, None )

    def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):

        logger = logging.getLogger( 'smtpcache.process' )

        msg = email.message_from_string( data.decode( 'utf-8' ) )

        logger.info( 'incoming message from: {}'.format( msg['From'] ) )

        with SMTP_SSL( self.out_server, self.out_port ) as smtp:
            print( smtp.login( self.out_user, self.out_password ) )
            print( smtp.sendmail( msg['From'], msg['To'], msg.as_string() ) )

