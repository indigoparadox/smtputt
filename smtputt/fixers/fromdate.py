
from email.message import EmailMessage
from email.utils import formatdate

from . import SMTPuttFixer

class SMTPuttFromDateFixer( SMTPuttFixer ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.from_addr = kwargs['fromaddress'] if 'fromaddress' in kwargs \
            else None

    def fix_message_date( self, msg ):
        self.logger.info( 'adding missing date field' )
        msg.add_header( 'Date', formatdate() )
        return msg

    def process_email( self, peer, msg : EmailMessage ):

        if self.from_addr:
            msg = self.fix_message_date( msg )

        return msg

FIXER = SMTPuttFromDateFixer
