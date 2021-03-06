
import unittest
import os
import sys

from faker import Faker

sys.path.append( os.path.dirname( __file__ ) )

from fake_smtp import FakeSMTP
from smtputt.authorization import SMTPuttAuthResult, dictauth
from smtputt.channel import SMTPuttChannel

class TestChannel( unittest.TestCase ):

    def setUp(self) -> None:

        self.fake = Faker()
        self.fake.add_provider( FakeSMTP )

        self.kwargs = {
            'authmodule': dictauth,
            'authrequired': 'true',
            'authdict': 'testuser1:testpass1,testuser2:testpass2'
        }

        self.channel = SMTPuttChannel( self, self, None )

        return super().setUp()

    def test_auth_validate( self ):

        res = self.channel.auth_validate_plain( 'testuser1', 'testpass1' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_OK )

        res = self.channel.auth_validate_plain( 'testuser2', 'testpass1' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_REJECTED )

        res = self.channel.auth_validate_login( 'testuser1' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_IN_PROGRESS )

        res = self.channel.auth_validate_login( 'badpass' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_REJECTED )

        res = self.channel.auth_validate_login( 'testuser1' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_IN_PROGRESS )

        res = self.channel.auth_validate_login( 'testpass1' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_OK )

    # Dummy connection methods.

    def getpeername( self ):
        return 'testpeer'

    def setblocking( self, blocking ):
        pass

    def fileno( self ):
        return 0

    def send( self, data ):
        pass

    def recv( self, sz ):
        pass

    def close( self ):
        pass
