
import os
import sys
import unittest
from unittest.mock import Mock, MagicMock

sys.path.append( os.path.dirname( __file__ ) )

import smtputt.svc

class TestSvc( unittest.TestCase ):

    def test_svc_start( self ):

        smtputt.svc.win32event = Mock()
        smtputt.svc.win32service = Mock()
        smtputt.svc.servicemanager = Mock()
        smtputt.svc.HandleCommandLine = Mock()
        #smtputt.svc.ServiceFramework = Mock()

        class TestingSMTPuttService( smtputt.svc.SMTPuttService ):
            def __init__( self ):
                pass

        svc = TestingSMTPuttService()
