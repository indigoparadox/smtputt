
from urllib.parse import urlparse

import ldap3

from . import SMTPuttAuthorizer, SMTPuttAuthResult

class SMTPuttLDAPAuthorizer( SMTPuttAuthorizer ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        server_args = {}

        ldap_url = urlparse( kwargs['ldapurl'] )

        server_args['host'] = ldap_url.hostname
        if ldap_url.port:
            server_args['port'] = ldap_url.port

        self.dn_format = kwargs['ldapdnformat']
        self.use_ssl = ('ldaps' == ldap_url.scheme)

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
