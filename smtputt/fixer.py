

from email.utils import formatdate
from smtputt.server import SMTPuttServer

class SMTPuttFixer( object ):

    def __init__( self, **kwargs ):
        self.from_addr = kwargs['fromaddress'] if 'fromaddress' in kwargs \
            else None
        self.server : SMTPuttServer

    def fix_message_from( self, msg ):
        self.logger.info( 'replacing from addres' )
        msg.replace_header( 'From', self.from_addr )
        return msg

    def fix_message_date( self, msg ):
        self.logger.info( 'adding missing date field' )
        msg.add_header( 'Date', formatdate() )
        return msg

    def process_email( self, peer, msg ):

        if self.from_addr:
            msg = self.fix_message_from( msg )

        if self.server and self.server.relay:
            self.server.relay.send_mail( msg )
