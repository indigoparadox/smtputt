
import logging
import asyncore
import re
import base64
from smtpd import SMTPChannel
from enum import Enum

from smtputt.authorization import SMTPuttAuthorizer, SMTPuttAuthResult

PATTERN_COMMAND = re.compile( b'(?P<command>[a-zA-Z]*)\\s*(?P<args>.*)' )
PATTERN_AUTH = re.compile( r'(?P<method>[A-Za-z0-9]*)\s*(?P<creds>.*)?' )

class SMTPuttAuthStatus( Enum ):
    AUTH_NONE = 0
    AUTH_IN_PROGRESS = 1
    AUTH_SUCCESSFUL = 2

class SMTPuttChannel( SMTPChannel ):

    commands_noauth = [b'AUTH', b'EHLO', b'HELO', b'NOOP', b'RSET', b'QUIT']

    def __init__( self, server, conn, addr,  *args, **kwargs ):

        self.logger = logging.getLogger( 'channel' )
        self._log_pfx = addr
        self.received_lines : list

        super().__init__( server, conn, addr, *args, **kwargs )

        self.auth_required = \
            ('authrequired' in server.kwargs and \
                server.kwargs['authrequired'])
        self.auth_class : SMTPuttAuthorizer
        self.auth_class = server.kwargs['authmodule'].AUTHORIZER \
            if 'authmodule' in server.kwargs else None
        assert( self.auth_class or not self.auth_required )

        # These are only used for LOGIN.
        self._auth_login_stage = SMTPuttAuthStatus.AUTH_NONE
        self._auth_login_user = None

        self.kwargs = server.kwargs

    def SMTP_QUIT( self, arg: str ):
        self.push( '221 Goodbye' )
        self.close_when_done()
        raise asyncore.ExitNow( 'QUIT received' )

    def smtp_EHLO( self, arg: str ):
        self.push( '250-localhost Hello {}'.format( arg ) )
        if self.auth_class:
            self.push( '250-AUTH LOGIN PLAIN' )
        super().smtp_EHLO( arg )

    def smtp_AUTH( self, arg: str ):

        match = PATTERN_AUTH.match( arg )

        if not match:
            self.push( '500 Error: bad syntax' )

        # Validate credentials based on auth method.
        groups = match.groups()
        method = groups[0]
        if 'PLAIN' == method.upper():
            user_pass = self.auth_parse_plain( groups[1] )
            res = self.auth_validate_plain( *user_pass )
        elif 'LOGIN' == method.upper():
            if 1 == len( groups ):
                self.push( '334 VXNlcm5hbWU6' ) # "Username"
                return
            user_pass = self.auth_parse_plain( groups[1] )
            res = self.auth_validate_login( user_pass[0] )

        # Decide what to do next.
        if res == SMTPuttAuthResult.AUTH_REJECTED:
            self.push( '535 Authentication credentials invalid' )
            self.auth_reset()
        elif SMTPuttAuthResult.AUTH_OK == res:
            self.push( '235 Authentication successful' )
            self.auth_success()
        elif SMTPuttAuthResult.AUTH_FAILED == res:
            self.push( '454 Temporary authentication failure' )
        elif SMTPuttAuthResult.AUTH_IN_PROGRESS:
            self.push( '334 UGFzc3dvcmQ6' ) # "Password"

    def auth_parse_plain( self, creds : str ):
        user_pass = base64.b64decode( creds ).decode( 'utf-8' )
        user_pass = user_pass.split( '\0' )
        while '' == user_pass[0]:
            user_pass.pop( 0 )
        return user_pass

    def auth_validate_login( self, cred : str ):
        if SMTPuttAuthStatus.AUTH_NONE == self._auth_login_stage:
            # First step.
            self._auth_login_user = cred
            self._auth_login_stage = SMTPuttAuthStatus.AUTH_IN_PROGRESS
            return SMTPuttAuthResult.AUTH_IN_PROGRESS

        elif SMTPuttAuthStatus.AUTH_IN_PROGRESS == self._auth_login_stage:
            # Second step.
            authorizer = self.auth_class( **self.kwargs )
            res = authorizer.authorize( self._auth_login_user, cred )
            self.auth_reset()
            return res

    def auth_validate_plain( self, user : str, passwd : str ) \
    -> SMTPuttAuthResult:
        self.auth_reset()
        authorizer = self.auth_class( **self.kwargs )
        return authorizer.authorize( user, passwd )

    def auth_success( self ):

        ''' Set status to authorized. '''

        self.auth_reset()
        self._auth_login_stage = SMTPuttAuthStatus.AUTH_SUCCESSFUL

    def auth_reset( self ):

        ''' Reset an auth in progress or cancel current auth. '''

        self._auth_login_stage = SMTPuttAuthStatus.AUTH_NONE
        self._auth_login_user = None

    def push( self, msg ):

        self.logger.debug( '%s: push: %s', self._log_pfx, msg )

        super().push( msg )

    def found_terminator( self ):
        if self.smtp_state != self.COMMAND:
            return super().found_terminator()

        line = self._emptystring.join( self.received_lines )
        self.logger.debug( '%s rcv: %s', self._log_pfx, line )
        match = PATTERN_COMMAND.match( line )
        if not match:
            self.push( '500 Error: bad syntax' )
        cmd = match.groups()[0]

        if SMTPuttAuthStatus.AUTH_IN_PROGRESS == self._auth_login_stage:
            # Most likely in stage 2 of login auth.
            # This is base64, so w/e, just decode it.
            self.smtp_AUTH( 'LOGIN ' + line.decode( 'utf-8' ) )
            self.received_lines = []
            return

        if self.auth_required and \
        SMTPuttAuthStatus.AUTH_SUCCESSFUL != self._auth_login_stage and \
        cmd.upper() not in self.commands_noauth:
            self.push( '503 Authentication required' )
            return

        super().found_terminator()
        