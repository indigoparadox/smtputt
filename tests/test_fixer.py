
import unittest
import email.message

from smtputt.fixers.fromaddress import SMTPuttFromAddressFixer
from smtputt.fixers.fromdate import SMTPuttFromDateFixer

class TestFixer( unittest.TestCase ):

    def test_fix_from_address( self ):

        msg = email.message.EmailMessage()
        msg.add_header( 'From', 'sender@example.com' )

        fixer_args = {
            'fromaddress': 'fixed@example.com'
        }
        fixer = SMTPuttFromAddressFixer( **fixer_args )

        msg_fixed = fixer.fix_message_from( msg )
        self.assertEqual( msg_fixed['From'], 'fixed@example.com' )

    def test_fix_date_heder( self ):

        msg = email.message.EmailMessage()
        msg.add_header( 'From', 'sender@example.com' )

        fixer = SMTPuttFromDateFixer()

        msg_fixed = fixer.fix_message_date( msg )
        self.assertIn( 'Date', msg_fixed )
