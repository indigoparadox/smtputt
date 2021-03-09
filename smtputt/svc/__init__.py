
from configparser import NoOptionError, NoSectionError
import os
import logging
from logging.handlers import NTEventLogHandler

win32event = None
win32service = None
servicemanager = None
ServiceFramework = object
HandleCommandLine = None

try:
    import win32event
    import win32service
    import servicemanager
    from win32serviceutil import ServiceFramework, HandleCommandLine
except ImportError:
    pass

from smtputt.config import load_config
from smtputt.server import SMTPuttServer

CONFIG_PATH = os.path.join( os.path.dirname( __file__ ), 'smtputt.ini' )

class SMTPuttService( ServiceFramework ):

    _svc_name_ = 'SMTPutt'
    _svc_display_name_ = 'SMTPutt Email Proxy'
    _svc_description_ = 'SMTP filter service to repair broken e-mails created by legacy software.'

    def __init__( self, args ):

        super().__init__( args )

        evthandler = NTEventLogHandler( 'SMTPutt' )
        logging.basicConfig( level=logging.INFO )
        logging.getLogger( '' ).addHandler( evthandler )
        self.logger = logging.getLogger( 'svc' )
        self.smtp_cache : SMTPuttServer

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

        try:
            server_cfg, module_cfgs = load_config( CONFIG_PATH )
        except (NoOptionError, NoSectionError, OSError, IOError) as exc:
            self.logger.error(
                'error loading config: %s; please see documentation for details',
                exc )

        self.smtp_cache = SMTPuttServer( module_cfgs, **server_cfg )
        cache_thread = self.smtp_cache.serve_thread()
        self.ReportServiceStatus( win32service.SERVICE_RUNNING )
        cache_thread.join()

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            ('SMTPutt', '') )
