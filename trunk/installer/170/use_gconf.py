import gconf
import os

def install(wallpaper_file):
    """Set the wallpaper_file as the current Gnome desktop background.
    """
    gclient = gconf.client_get_default()
    if gclient:
        old_file = gclient.get_string(
            '/desktop/gnome/background/picture_filename')
        if os.path.basename(os.path.realpath(old_file)) != os.path.basename(
            os.path.realpath(wallpaper_file)):
            return gclient.set_string(
                '/desktop/gnome/background/picture_filename',
                os.path.realpath(wallpaper_file))
