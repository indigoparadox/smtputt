
from email.message import EmailMessage
from email.utils import formatdate

from . import SMTPuttFixer

class SMTPuttFromDateFixer( SMTPuttFixer ):

    def fix_message_date( self, msg ):
        self.logger.info( 'adding missing date field' )
        msg.add_header( 'Date', formatdate() )
        return msg

    def process_email( self, peer, msg : EmailMessage ):

        msg = self.fix_message_date( msg )

        return msg

FIXER = SMTPuttFromDateFixer
