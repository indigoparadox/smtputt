
from email.message import EmailMessage
import logging
from email.utils import formatdate

class SMTPuttFixer( object ):

    def __init__( self, **kwargs ):
        self.from_addr = kwargs['fromaddress'] if 'fromaddress' in kwargs \
            else None
        self.logger = logging.getLogger( 'fixer' )
        self.server = None

    def fix_message_from( self, msg ):
        self.logger.info( 'replacing from addres' )
        msg.replace_header( 'From', self.from_addr )
        return msg

    def fix_message_date( self, msg ):
        self.logger.info( 'adding missing date field' )
        msg.add_header( 'Date', formatdate() )
        return msg

    def process_email( self, peer, msg : EmailMessage ):

        if self.from_addr:
            msg = self.fix_message_from( msg )
        
        if 'Date' not in msg:
            msg = self.fix_message_date( msg )

        if self.server and self.server.relay:
            self.server.relay.send_email( msg )

        return msg
