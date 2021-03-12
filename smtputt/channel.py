
import logging
import asyncore
import re
import base64
import binascii
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

        # These are only used for LOGIN.
        self._auth_login_stage = SMTPuttAuthStatus.AUTH_NONE
        self._auth_login_user = None

        self.auth_required = \
            ('authrequired' in server.kwargs and \
                server.kwargs['authrequired'])
        self.auth_classes : 'list[SMTPuttAuthorizer]'
        self.auth_classes = \
            [m.AUTHORIZER( **server.module_cfgs[m.__loader__.name] ) \
            for m in server.auth_modules]
        assert( self.auth_classes or not self.auth_required )

        self.kwargs = server.kwargs

        super().__init__( server, conn, addr, *args, **kwargs )

    def handle_close( self ):
        try:
            self.smtp_server.channels.remove( self )
        except AttributeError as exc:
            self.logger.warning(
                'while removing self from server channels: %s', exc )
        super().handle_close()

    def SMTP_QUIT( self, arg: str ):
        self.push( '221 Goodbye' )
        self.close_when_done()
        raise asyncore.ExitNow( 'QUIT received' )

    def smtp_EHLO( self, arg: str ):
        self.push( '250-localhost Hello {}'.format( arg ) )
        if self.auth_classes:
            self.push( '250-AUTH LOGIN PLAIN' )
        super().smtp_EHLO( arg )

    def smtp_AUTH( self, arg: str ):

        if not arg:
            self.push( '500 Error: bad syntax' )
            return

        match = PATTERN_AUTH.match( arg )

        if not match:
            self.push( '500 Error: bad syntax' )

        # Validate credentials based on auth method.
        groups = match.groups()
        method = groups[0]
        if 'PLAIN' == method.upper():
            user_pass = self.auth_parse_plain( groups[1] )
            if len( user_pass ) < 2:
                self.auth_reset()
                self.push( '535 Authentication credentials invalid' )
                return
            res = self.auth_validate_plain( *user_pass )
        elif 'LOGIN' == method.upper():
            # Get rid of initial ''.
            while 1 <= len( groups ) and '' == groups[0]:
                groups.pop( 0 )
            if 1 == len( groups ) or '' == groups[1]:
                self.push( '334 VXNlcm5hbWU6' ) # "Username"
                self._auth_login_stage = SMTPuttAuthStatus.AUTH_IN_PROGRESS
                return
            user_pass = self.auth_parse_plain( groups[1] )
            if 1 <= len( user_pass ):
                res = self.auth_validate_login( user_pass[0] )
            else:
                self.auth_reset()
                self.push( '535 Authentication credentials invalid' )
                return

        # Decide what to do next.
        if res == SMTPuttAuthResult.AUTH_REJECTED:
            self.push( '535 Authentication credentials invalid' )
            self.auth_reset()
        elif SMTPuttAuthResult.AUTH_OK == res:
            self.push( '235 Authentication successful' )
            self.auth_success()
        elif SMTPuttAuthResult.AUTH_FAILED == res:
            self.push( '454 Temporary authentication failure' )
        elif SMTPuttAuthResult.AUTH_IN_PROGRESS == res:
            self.push( '334 UGFzc3dvcmQ6' ) # "Password"

    def auth_parse_plain( self, creds : str ):
        user_pass = ''
        try:
            user_pass = base64.b64decode( creds ).decode( 'utf-8' )
        except binascii.Error:
            user_pass = creds
        user_pass = user_pass.split( '\0' )
        # Get rid of initial ''.
        while 1 <= len( user_pass ) and '' == user_pass[0]:
            user_pass.pop( 0 )
        return user_pass

    def auth_validate_login( self, cred : str ):
        if not self._auth_login_user:
            # First step.
            self._auth_login_user = cred
            self._auth_login_stage = SMTPuttAuthStatus.AUTH_IN_PROGRESS
            return SMTPuttAuthResult.AUTH_IN_PROGRESS

        elif SMTPuttAuthStatus.AUTH_IN_PROGRESS == self._auth_login_stage:
            # Second step.
            for authorizer in self.auth_classes:
                res = None
                try:
                    res = authorizer.authorize( self._auth_login_user, cred )
                except Exception as exc:
                    self.logger.error( 'while authorizing: %s', exc )
                    res = SMTPuttAuthResult.AUTH_FAILED
                self.auth_reset()
                if SMTPuttAuthResult.AUTH_REJECTED != res:
                    # Break immediately on success or technical issue.
                    return res
            return res

    def auth_validate_plain( self, user : str, passwd : str ) \
    -> SMTPuttAuthResult:
        for authorizer in self.auth_classes:
            try:
                res = authorizer.authorize( user, passwd )
            except Exception as exc:
                self.logger.error( 'while authorizing: %s', exc )
                res = SMTPuttAuthResult.AUTH_FAILED
            self.auth_reset()
            if SMTPuttAuthResult.AUTH_REJECTED != res:
                # Break immediately on success or technical issue.
                return res
        return res

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
            super().found_terminator()
            return

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
        