
from smtputt.smtpcache import SMTPCache
import asyncore
import logging
import json
import win32event
import socket
import win32service
import sys
import os
#import pywin32types
from win32serviceutil import ServiceFramework, HandleCommandLine
from logging.handlers import NTEventLogHandler
from threading import Thread

class SMTPuttService( ServiceFramework ):

    _svc_name_ = 'SMTPutt'
    _svc_display_name_ = 'SMTPutt Email Proxy'
    _svc_description_ = 'SMTP filter service to repair broken e-mails created by legacy software.'

    def __init__( self, args ):

        ServiceFramework.__init__( self, args )
        
        evthandler = NTEventLogHandler( 'SMTPutt' )
        logging.basicConfig( level=logging.INFO )
        logger = logging.getLogger( '' )
        logger.addHandler( evthandler )

        self.hWaitStop = win32event.CreateEvent( None, 0, 0, None )
        #self.overlapped = pywintypes.OVERLAPPED()
        #self.overlapped.hEvent = win32event.CreateEvent( None, 0, 0, None )
        #socket.setdefaulttimeout( 60 )
        
        self.ReportServiceStatus( win32service.SERVICE_START_PENDING )

    @classmethod
    def handle_cmd( cls ):
        HandleCommandLine( cls )

    def SvcStop( self ):
        self.ReportServiceStatus( win32service.SERVICE_STOP_PENDING )

        try:
            self.smtp_cache.close()
            #self.smtp_thread.join()
        except Exception as e:
            logger.error( e )

        self.ReportServiceStatus( win32service.SERVICE_STOPPED )
        win32event.SetEvent( self.hWaitStop )

    def SvcDoRun( self ):
        logger = logging.getLogger( 'smtpcache.svc' )

        logger.info( 'using {} as config...'.format(
            os.path.join( os.getcwd(), 'smtputt.ini' ) ) )

        config = configparser.ConfigParser()
        config.read( os.path.join( os.getcwd(), 'smtputt.ini' ) )
        cfg_dict = dict( config.items( 'forwarder' ) )

        self.smtp_cache = SMTPCache( **cfg_dict )

        self.ReportServiceStatus( win32service.SERVICE_RUNNING )

        logger.info( 'service intialized; sending mail to {} as {}; beginning loop'.format(
            config['server'], config['from_addr'] ) )
        
        #self.smtp_thread = Thread( target=asyncore.loop, kwargs={'timeout': 1} )
        #self.smtp_thread.start()
        asyncore.loop()

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            ('SMTPutt', '') )

if '__main__' == __name__:
    if len( sys.argv ) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle( SMTPuttService )
        servicemanager.StartServiceCtrlDispatcher()
    else:
        SMTPuttService.handle_cmd()
    
