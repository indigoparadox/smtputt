
from email.message import EmailMessage

from . import SMTPuttFixer

class SMTPuttFromAddressFixer( SMTPuttFixer ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.from_addr = kwargs['fromaddress'] if 'fromaddress' in kwargs \
            else None

    def fix_message_from( self, msg ):
        self.logger.info( 'replacing from addres' )
        msg.replace_header( 'From', self.from_addr )
        return msg

    def process_email( self, peer, msg : EmailMessage ):

        if self.from_addr:
            msg = self.fix_message_from( msg )

        return msg

FIXER = SMTPuttFromAddressFixer
