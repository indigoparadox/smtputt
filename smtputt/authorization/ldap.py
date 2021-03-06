
import ldap3

from . import SMTPuttAuthorizer, SMTPuttAuthResult

class SMTPuttLDAPAuthorizer( SMTPuttAuthorizer ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        server_args = {}

        server_args['host'] = kwargs['ldaphost']
        if 'ldapport' in kwargs:
            server_args['port'] = int( kwargs['ldapport'] )

        self.dn_format = kwargs['ldapdnformat']
        self.use_ssl = ('ldapssl' in kwargs and kwargs['ldapssl'])

        self.server = ldap3.Server( **server_args )

    def authorize( self, username, password ):

        connection_args = {}

        connection_args['server'] = self.server
        connection_args['user'] = self.dn_format.replace( '%u', username )
        connection_args['password'] = password
        connection_args['client_strategy'] = ldap3.SAFE_SYNC

        connection = ldap3.Connection( **connection_args )

        if self.use_ssl:
            connection.start_tls()

        status, result, response, request = connection.bind()
        if status:
            return SMTPuttAuthResult.AUTH_OK
        else:
            return SMTPuttAuthResult.AUTH_REJECTED

AUTHORIZER = SMTPuttLDAPAuthorizer
