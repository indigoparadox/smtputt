
import os
import sys
import unittest
from unittest.mock import Mock

sys.path.append( os.path.dirname( __file__ ) )

import smtputt.authorization.ldap
from smtputt.authorization import SMTPuttAuthResult

class TestAuth( unittest.TestCase ):

    def setUp( self ):
        pass

    def test_auth_ldap( self ):
        mock_ldap = Mock()
        mock_connection = mock_ldap.Connection.return_value
        mock_connection.bind.return_value = True, {}, None, {}

        smtputt.authorization.ldap.ldap3 = mock_ldap
        args = {
            'ldapurl': 'ldaps://ldap.example.com',
            'ldapdnformat': 'uid=%u,ou=binders,dc=example,dc=com'
        }
        auth = smtputt.authorization.ldap.SMTPuttLDAPAuthorizer( **args )
        res = auth.authorize( 'testuser1', 'testpass1' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_OK )

        mock_connection.bind.return_value = False, {}, None, {}

        res = auth.authorize( 'testuser1', 'testpass2' )
        self.assertEqual( res, SMTPuttAuthResult.AUTH_REJECTED )
        mock_connection.bind.assert_called()
