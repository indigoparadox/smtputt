
import logging
from email.message import EmailMessage

class SMTPuttFixer( object ):

    def __init__( self, **kwargs ):
        self.logger = logging.getLogger( 'fixer' )

    def process_email( self, peer, msg : EmailMessage ):

        return msg
