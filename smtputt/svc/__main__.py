
import sys

import servicemanager

from . import SMTPuttService

def main():

    if len( sys.argv ) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle( SMTPuttService )
        servicemanager.StartServiceCtrlDispatcher()
    else:
        SMTPuttService.handle_cmd()

if '__main__' == __name__:
    main()
