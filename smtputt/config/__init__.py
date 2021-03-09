
import logging
import os
import shutil
import sys
import configparser

CONFIGURATION_PATHS=[
    '/etc/smtputt.ini',
    os.path.join( os.path.expanduser( '~' ), '.smtputt.ini' )
]

def load_config( config_path ):
    config = configparser.ConfigParser()
    config.read( config_path )
    module_cfgs = {}
    server_cfg = dict( config.items( 'server' ) )
    for module in server_cfg['authmodules'].split( ',' ):
        module_cfgs[module] = dict( config.items( module ) )
    for module in server_cfg['relaymodules'].split( ',' ):
        module_cfgs[module] = dict( config.items( module ) )
    for module in server_cfg['fixermodules'].split( ',' ):
        module_cfgs[module] = dict( config.items( module ) )

    return server_cfg, module_cfgs

def load_or_create_config( create_on_fail=False, paths=None ):

    logger = logging.getLogger( 'config' )

    if not paths:
        paths = CONFIGURATION_PATHS

    for path_iter in paths:
        logger.debug( 'searching for config in %s...', path_iter )
        if os.path.exists( path_iter ):
            return load_config( path_iter )

    # If we're still here, no config was found.
    if create_on_fail:
        for path_iter in paths:
            try:
                logger.debug(
                    'attempting to copy example config to %s...', path_iter )
                shutil.copy(
                    os.path.join( os.path.dirname( __file__ ), 'smtputt.ini.dist' ),
                    path_iter )
                logger.info( 'example configuration copied to %s', path_iter )
                logger.info( 'see documentation for details' )
                sys.exit( 1 )
            except (IOError, OSError) as exc:
                logger.error( 'unable to copy config: %s', exc )
                continue

    logger.error(
        'no valid configuration found; see documentation for details' )
    sys.exit( 1 )
