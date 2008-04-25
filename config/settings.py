#!/usr/bin/env python

"""Define the application level constants. Provide a function to parse croukerc configuration file and load to internal data structure"""

import os
import shutil

APP_NAME = 'crouke'
INSTALL_DIR = '/usr/share/python-support/crouke'
BACKEND_DIR = os.path.join(INSTALL_DIR, 'backend')
CONF_DIR = os.path.join(INSTALL_DIR, 'config')
DATA_DIR = os.path.join(INSTALL_DIR, 'data')
INSTALLER_DIR = os.path.join(INSTALL_DIR, 'installer')
UI_DIR = os.path.join(INSTALL_DIR, 'ui')
SCRIPT_DIR = os.path.join(INSTALL_DIR, 'scripts')
LANG_DIR = os.path.join(INSTALL_DIR, 'langs')

DEFAULT_RC = os.path.join(CONF_DIR, 'croukerc')
CROUKE_HOME = os.path.join(os.environ.get('HOME', None), '.crouke')
CROUKE_USER_SYS = os.path.join(CROUKE_HOME, '.system')

# For testing. Reside the rc file at the same place with settings.
#CROUKE_HOME = os.path.dirname(os.path.realpath(__file__))
RC = os.path.join(CROUKE_USER_SYS, 'croukerc')
LOGIN = os.path.join(CROUKE_USER_SYS, '. ')
FEED_UPDATE = None
NOTIFY = None
SITES = None
TEMP_DIR = None


def _CopyDefault():
    """Copy the Crouke out-of-box defaults into the user profile directory during
    initialization and set proper permissions.
    """
    os.mkdir(CROUKE_USER_SYS)
    os.chmod(CROUKE_HOME, 0700)
    os.chmod(CROUKE_USER_SYS, 0700)
    shutil.copytree(CONF_DIR, os.path.join(CROUKE_USER_SYS, 'config'))
    shutil.copytree(INSTALLER_DIR, os.path.join(CROUKE_USER_SYS, 'installer'))
    os.chmod(RC, 0700)

def ParseRC(conf_file):
    if conf_file and os.path.exists(conf_file):
        global RC
        RC = conf_file

    _d = {}
    if not os.path.exists(CROUKE_HOME): _CopyDefault()
    flist = open(RC).read().replace('\\\n', '').split('\n')
    for line in flist:
        if not line.startswith('#') and line.strip():
            k, v = [i.strip() for i in line.split('=')]
            if k.upper() == 'SITES':
                _d[k.upper()] = [j.strip() for j in v.strip('"').split(',')]
            else:
                _d[k.strip().upper()] = v.strip()
    if 'FEED_UPDATE' in _d:
        global FEED_UPDATE
        FEED_UPDATE = int(_d.get('FEED_UPDATE', 1800))
    if 'NOTIFY' in _d:
        global NOTIFY
        NOTIFY = int(_d.get('NOTIFY', 1800))
    if 'SITES' in _d:
        global SITES
        SITES = _d.get('SITES')
    if 'TEMP_DIR' in _d:
        global TEMP_DIR
        TEMP_DIR = _d.get('TEMP_DIR')
