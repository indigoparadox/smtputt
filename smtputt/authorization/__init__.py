
from enum import Enum

class SMTPuttAuthResult( Enum ):
    AUTH_OK = 0
    AUTH_REJECTED = 1
    AUTH_FAILED = 2
    AUTH_IN_PROGRESS = 3

class SMTPuttAuthorizer( object ):

    def __init__( self, **kwargs ):
        pass

    def authorize( self, username, password ) -> SMTPuttAuthResult:
        return SMTPuttAuthResult.AUTH_OK
