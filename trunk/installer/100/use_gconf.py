import bz2
import gconf
import glob
from gzip import GzipFile
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

import sys
sys.path.append('../../')
from config import settings
from config import texts as _
import excepts

def _InstallFromCurrentDir(gconf_client, cur_dir, target_dir, target_file):
    """
    """
    # tempd contains the index.theme which means
    # it is already the top level of the real icon theme dir
    icon_dir = target_file.split('.')[0]
    shutil.copytree(cur_dir, os.path.join(target_dir, icon_dir))
    os.symlink(os.path.join(target_dir, icon_dir),
               os.path.join(os.environ.get('HOME'), '.themes', icon_dir))
    gconf_client.set_string('/desktop/gnome/interface/gtk_theme', icon_dir)


def _InstallFromSubdirs(gconf_client, dirs, target_dir):
    """
    """
    for d in dirs:
        if glob.glob1(d, 'index.theme'):
            shutil.copytree(d, os.path.join(target_dir, d))
            os.symlink(os.path.join(target_dir, d),
                       os.path.join(os.environ.get('HOME'), '.themes', d))
            # If an archive contains multiple icon themes,
            # then this release only applies the first one.
            gconf_client.set_string('/desktop/gnome/interface/gtk_theme', d)
            return
    raise excepts.InstallError(_.sub_inst_failed)


def install(icon_archive_file):
    """Instal an icon theme package.

    Successful installation return None, failed/error install return failure
    message or raise exceptions.

    Args:
        icon_archive_file: full obsolute path for the icon archive file.

    Returns:
        Successful installation return None, failed/error install return failure
        message or raise exceptions.
    """
    target_dir = os.path.dirname(icon_archive_file)
    target_basefile = os.path.basename(icon_archive_file)
    gclient = gconf.client_get_default()

    # if the archive is a tar.(gz|bz2) file
    if tarfile.is_tarfile(icon_archive_file):
        tempd = tempfile.mkdtemp(dir=settings.TEMP_DIR)
        os.chdir(tempd)
        tarfile.open(icon_archive_file).extractall()
        subdirs = os.listdir('.')
        if glob.glob1('.', 'index.theme'):
            _InstallFromCurrentDir(gclient, tempd, target_dir, target_basefile) 
        else:
            if subdirs:
                _InstallFromSubdirs(subdirs, target_dir)

            # If current dir does not contain index.theme and there is no
            # subdirs contains the file or no subdirs, then we can use
            # gconf to install.
            else:
                raise excepts.InstallError(_.inst_failed)
        
        # clean the environment
        # only do clean when the installation is successful
        os.chdir(target_dir)
        os.unlink(tempd)
        os.unlink(icon_archive_file)
        return

    # if the archive is a pure zip file. (Winzip type)
    # several possibilities can happen when encountering a zip file 
    # 1. the zip is a shell containing the actual theme package.
    # 2. the zip is a shell containing several theme packages.
    # 3. the zip itself contains the theme package.
    # In 1/2 situation, one or more tar.(gz|bz2) packages might be found.
    # We do not conside any weird situation where like zip contains another zip
    # or tar contains zip, then tar, zip...
    if zipfile.is_zipfile(icon_archive_file):
        tempd = tempfile.mkdtemp(dir=settings.TEMP_DIR)
        os.chdir(tempd)
        f = subprocess.Popen(['unzip', '-o', icon_archive_file],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)
        if glob.glob1('.', 'index.theme'):
            _InstallFromCurrentDir(gclient, tempd, target_dir, target_basefile)
        else:
            subdirs = os.listdir('.')
            if not subdirs:
                raise excepts.InstallError(f.stdout.read())
            else:
                for d in subdirs:
                    os.chdir(d)
                    # if sub directory contains tar.(gz|bz2) packages
                    # then those will be the target icon package to install
                    tar_packages = glob.glob1('.', '*.tar*')
                    if tar_packages:
                        for t in tar_packages:
                            install(os.path.join(target_dir, d, t))
                    else:
                        # Otherwise, see if the subdir itself contains index.theme
                        # file.
                        _InstallFromCurrentDir(gclient, d, target_dir, target_basefile)
                    os.chdir('..')

        # clean the environment
        os.chdir(target_dir)
        os.unlink(tempd)
        os.unlink(icon_archive_file)
        return

    # At last, handle the file using pure gzip format or bz2 format.
    # If the unzipped target isn't a archive file, then an error will be raised.
    ext = os.path.splitext(icon_archive_file)[-1]
    file = target_basefile.split('.')[0]
    if ext in ['.gz', '.tgz', '.taz', '-gz', 'z', '-z', '_z', '.Z']:
        # if a file ext is those exts list, then it is possibe that gunzip 
        # can unzip it.
        zipf = gzip.GzipFile(icon_archive_file)
        # use the original basefile's basename as the unzipped target
        open(file, 'wb').write(gzip.GzipFile(icon_archive_file).read())
    elif ext in ['.bz2', '.bz', '.tbz2', '.tbz']:
        open(file, 'wb').write(bz2.decompress(open(icon_archive_file).read()))
    else:
        # the original file is left in the download dir untouched.
        # the user can manually do the installation if wanted.
        raise excepts.InstallError(_.unknown_file)
    return install(os.path.join(target_dir, file))

