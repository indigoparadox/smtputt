
import asyncore
import random
import email
import email.message
import time
from smtpd import SMTPServer
from threading import Thread
from contextlib import contextmanager

from smtputt.server import SMTPuttServer

        
@contextmanager
def create_test_server():
    test_server = None
    while not test_server:
        try:
            test_server = TestSMTPServer()
        except OSError:
            # Port in use.
            pass
    try:
        yield test_server
    finally:
        time.sleep( 1 )
        test_server.close()

class TestSMTPServer( SMTPServer ):

    def __init__( self ):
        self.smtp_listen = random.randrange( 40000, 50000 )
        super().__init__( ('localhost', self.smtp_listen), None )
        self.last_msg = None
        self.thread = Thread( target=asyncore.loop, daemon=True )
        self.thread.start()

    def process_message( self, peer, mailfrom, rcpttos, data, **kwargs ):
        msg = email.message_from_bytes( data )
        self.last_msg = msg
