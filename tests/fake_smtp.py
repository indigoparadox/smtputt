
from email.message import EmailMessage
from faker.providers import BaseProvider
from faker.providers.lorem import Provider as LoremProvider
from faker.providers.internet import Provider as InternetProvider

class FakeSMTP( InternetProvider, LoremProvider ):

    def email_msg( self ):

        msg = EmailMessage()
        msg.add_header( 'To', self.free_email() )
        msg.add_header( 'From', 'smtputt@{}'.format( self.free_email_domain() ) )
        msg.set_content( '\r\n'.join( [self.paragraph( 3, True, ['foo'] ) for i in range( 4 )] ) )

        return msg
