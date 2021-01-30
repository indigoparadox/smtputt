
from smtpd import SMTPServer
from smtplib import SMTP_SSL
from email.utils import formatdate
import email
import logging

class SMTPCache( SMTPServer ):

    def __init__( self, **kwargs ):
        self.out_server = kwargs['remoteserver']
        self.out_port = int( kwargs['remoteport'] ) if 'remoteport' in kwargs \
            else 25
        self.out_user = kwargs['remoteuser'] if 'remoteuser' in kwargs \
            else None
        self.out_password = kwargs['remotepassword'] if 'remotepassword' \
            in kwargs else None
        self.from_addr = kwargs['fromaddress'] if 'fromaddress' in kwargs \
            else self._default_from()

        listen_tuple = (
            kwargs['listenhost'] if 'listenhost' in kwargs else '0.0.0.0',
            int( kwargs['listenport'] ) if 'listenport' in kwargs else 25)

        super().__init__( listen_tuple, None )

    def _default_from( self ):
        logger = logging.getLogger( 'smtpcache.from' )
        logger.warn( 'using default from address; this should be changed!' )
        return 'smtputt@interfinitydynamics.info'

    def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):

        logger = logging.getLogger( 'smtpcache.process' )

        logger.info( 'connection established...' )

        msg = email.message_from_string( data.decode( 'utf-8' ) )

        msg.replace_header( 'From', self.from_addr )
        msg.add_header( 'Date', formatdate() )

        logger.info( 'incoming message from {} to {}'.format(
            msg['From'], msg['To'] ) )

        with SMTP_SSL( self.out_server, self.out_port ) as smtp:
            smtp.login( self.out_user, self.out_password )
            try:
                res = smtp.sendmail( 
                self.from_addr, msg['To'], msg.as_string() )
                logger.info( 'message forwarded without error.' )
            except Exception as e:
                logger.error( e )

