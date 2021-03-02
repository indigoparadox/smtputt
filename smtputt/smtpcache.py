
from smtpd import SMTPServer
from smtplib import SMTP_SSL
import email
import logging

class SMTPCache( SMTPServer ):

    def _default_from( self ):
        logger = logging.getLogger( 'smtpcache.from' )
        logger.warn( 'using default from address; this should be changed!' )
        return 'smtputt@interfinitydynamics.info'



        

