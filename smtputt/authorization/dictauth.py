
from . import SMTPuttAuthResult, SMTPuttAuthorizer

class SMTPuttDictAuthorizer( SMTPuttAuthorizer ):
    
    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.auth_dict = {}
        if 'authdict' in kwargs and isinstance( kwargs['authdict'], str ):
            for pair in kwargs['authdict'].split( ',' ):
                user_pass = pair.split( ':' )
                self.auth_dict[user_pass[0]] = user_pass[1]

    def authorize( self, username, password ):
        if username in self.auth_dict and \
        password == self.auth_dict[username]:
            return SMTPuttAuthResult.AUTH_OK
        else:
            return SMTPuttAuthResult.AUTH_REJECTED

AUTHORIZER = SMTPuttDictAuthorizer
