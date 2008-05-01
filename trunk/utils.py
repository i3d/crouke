#!/usr/bin/env python

# System library
import base64
import glob
import pickle
from optparse import OptionParser
import os
import threading

# Crouke library
from config import settings
import excepts

CATEGORY = os.path.join(settings.CROUKE_USER_SYS, 'config/category')
TEMP_CATEGORY = os.path.join(settings.CROUKE_USER_SYS, 'config/category.temp')

_installers = {}
_d = pickle.load(open(CATEGORY))
_rd = dict((v, k) for k, v in _d.iteritems())


class Installer(object):
    """Class to reprsent the installer filesystem structure.

    Provides methods:
        LoadInstaller: Load local installer modules.
        GetInstaller: Get a list of installer for a particular category.
        GetIdFromName: Get a Category Id from its name.
        GetNameFromId: Get a Gategory name from its Id.
        SyncCategory: Sync the remote category dict with the local cache.
    """
    _lock = threading.Lock()

    @classmethod
    def LoadInstaller(cls):
        """Load all locally available installers.
        """
        _submod_dirs = os.listdir('installer')
        if _submod_dirs:
            for name in _submod_dirs:
                # installers directories are named using the category ids.
                cate_id = os.path.basename(name)
                # installer modules for a category are python modules
                # that does not start with '_' in their file name.
                _files = [i for i in glob.glob(os.path.join(
                          'installer', name, '*.py'))
                          if not os.path.basename(i).startswith('_')]
                if _files:
                    for i in _files:
                        modu = __import__(i.replace('.py', '').replace(
                                          '/', '.'), {}, {}, [os.path.dirname(
                                          i).replace('/', '.')])
                        if cate_id not in _installers:
                            _installers[cate_id] = [modu]
                        else:
                            _installers[cate_id].append(modu)

    @classmethod
    def GetInstaller(cls, category_id):
        """Return a set of available installer modules for a given category.

        Args:
            category_id: the category id.

        Returns:
            A set of installer modules can be used. None if no such category id.
        """
        if not _installers: cls.LoadInstaller()
        return _installers.get(category_id, None)

    @classmethod
    def GetIdFromName(cls, name):
        """Get the category id by looking up the category name.

        Args:
            name: the category name.

        Returns:
            a category id string or None if no such name.
        """
        return _rd.get(name, None)

    @classmethod
    def GetNameFromId(cls, cate_id):
        """Get the category name by looking up the category id.

        Args:
            cate_id: the category id string.

        Returns:
            a category name or None if no such id.
        """
        return _d.get(cate_id, None)

    @classmethod
    def SyncCategory(cls, cate_dict):
        """Sync the category dict with the runtime/local cache.

        Thread-safe.

        Args:
            cate_dict: the category dictionary. May be pulled from all the websites.
        """
        cls._lock.acquire()
        try:
            try:
                # make a copy first in case anything wrong.
                open(TEMP_CATEGORY, 'wb').write(open(CATEGORY).read())
            except IOError:
                # If we can't write to the dir, then sync will not continue
                return False
            else:
                try:
                    try:
                        # dump the new category dictionary.
                        pickle.dump(cate_dict, open(CATEGORY, 'wb'))
                    except (PickleError, PicklingError, TypeError, StopIteration,
                            AttributeError, KeyError, ValueError, RuntimeError,
                            IOError):
                        # If any aboved exceptions raised, load back the old
                        # category file.
                        open(CATEGORY, 'wb').write(
                            open(TEMP_CATEGORY).read())
                    else:
                        # if dump successful
                        # 1. Update the runtime dictionary
                        global _d, _rd
                        _d = cate_dict
                        _rd = dict((v, k) for k, v in cate_dict.iteritems())

                        # 2. Add new category installer dirs if needed
                        _UpdateInstaller(_d)
                finally:
                    os.unlink(TEMP_CATEGORY)
        finally:
            cls._lock.release()


def _UpdateInstaller(cate_dict):
    """Update the installer filesystem structure and runtime installer modules
    with any updates needed.

    Since its an internal function and called from the SyncCategory method
    which is wrapped with lock, this function is also thread-safe.

    Args:
        cate_dict: the category dictionary.
    """
    dirs = os.listdir('installer')
    new_cate = set(cate_dict.keys()) - set(dirs)
    if new_cate:
        for cate in new_cate:
            os.makedir(os.path.join('installer', cate))
            open(os.path.join('installer', cate, '__init__.py'), 'wb')
        global _installers
        _installers = {}
        Installer.LoadInstaller()


def ParseOptions(argv):
    """
    """
    parser = OptionParser()
    parser.add_option('--disable_tray', dest='enable_tray', default=True,
                      action='store_false',
                      help='Run Crouke and load the tray icon. '
                      'This is the default action.')
    parser.add_option('--disable_animate', dest='animate', default=True,
                      action='store_false',
                      help='With tray icon animation.')
    parser.add_option('-c', '--conf', dest='conf_file', default=None,
                      help='Optional Crouke configuration file.')
    return parser.parse_args(argv)


class LogInToken(object):
    """
    """
    def __init__(self, user=None, password=None):
        """
        """
        self.__user = user
        self.__password = password

    def Load(self):
        try:
            f = open(settings.LOGIN)
        except IOError, e:
            raise excepts.LoadLoginCacheError(e)
        else:
            up = [i.strip('\n') for i in f]
            self.__user = base64.b64decode(up[0])
            self.__password = base64.b64decode(up[1])

    def Save(self):
        try:
            open(settings.LOGIN, 'wb').write(
                base64.b64encode(self.__user) + '\n' +
                base64.b64encode(self.__password))
        except IOError, e:
            raise excepts.SaveLoginTokenError(e)
        else:
            os.chmod(settings.LOGIN, 0600)

    def GetToken(self):
        return (self.__user, self.__password)

    def SetToken(self, user, password):
        self.__user = user
        self.__password = password

    @classmethod
    def HasLoginCache(cls):
        return os.path.exists(settings.LOGIN)
