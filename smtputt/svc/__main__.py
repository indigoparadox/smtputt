
import logging
import sys
import os
from logging.handlers import NTEventLogHandler

import win32event
import win32service
from win32serviceutil import ServiceFramework, HandleCommandLine

from smtputt import load_config
from smtputt.server import SMTPuttServer

# TODO: Dynamically determine this.
CONFIG_PATH = 'c:\\smtputt-master\\src\\smtputt.ini'

class SMTPuttService( ServiceFramework ):

    _svc_name_ = 'SMTPutt'
    _svc_display_name_ = 'SMTPutt Email Proxy'
    _svc_description_ = 'SMTP filter service to repair broken e-mails created by legacy software.'

    def __init__( self, args ):

        ServiceFramework.__init__( self, args )

        evthandler = NTEventLogHandler( 'SMTPutt' )
        logging.basicConfig( level=logging.INFO )
        logging.getLogger( '' ).addHandler( evthandler )
        self.logger = logging.getLogger( 'svc' )

        self.hWaitStop = win32event.CreateEvent( None, 0, 0, None )

        self.ReportServiceStatus( win32service.SERVICE_START_PENDING )

    @classmethod
    def handle_cmd( cls ):
        HandleCommandLine( cls )

    def SvcStop( self ):
        self.ReportServiceStatus( win32service.SERVICE_STOP_PENDING )

        try:
            self.smtp_cache.close()
        except Exception as e:
            self.logger.error( e )

        self.ReportServiceStatus( win32service.SERVICE_STOPPED )
        win32event.SetEvent( self.hWaitStop )

    def SvcDoRun( self ):

        self.logger.info( 'using %s as config...', CONFIG_PATH )

        server_cfg, module_cfgs = load_config( CONFIG_PATH )

        cache = SMTPuttServer( module_cfgs, **server_cfg )
        cache_thread = cache.serve_thread()
        self.ReportServiceStatus( win32service.SERVICE_RUNNING )
        cache_thread.join()

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            ('SMTPutt', '') )

def main():

    if len( sys.argv ) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle( SMTPuttService )
        servicemanager.StartServiceCtrlDispatcher()
    else:
        SMTPuttService.handle_cmd()

if '__main__' == __name__:
    main()
