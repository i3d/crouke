#/usr/bin/env python

"""Crouke's tray icon UI. Crouke is designed to start as a system tray icon and run
on the background. The main UI can be invoked by clicking the icon or if you want,
call the croukeui script."""

# System library
import gtk
import os
import sys
import time
    
# Crouke UI module
import croukeui
import utils
from config import settings
from config import texts as _

USE_EGG = False
    
# Check to see if we have a rather old gtk version. If so, we use egg.
if gtk.gtk_version < (2, 10, 0):
    try:
        import egg.trayicon
    except ImportError, e:
        print >> sys.stderr, e
        sys.exit(1) 
    else:
        USE_EGG = True
    

class TrayIcon(object):
    """ """
    
    def __init__(self, enable_tray=True, animate=True, conf_file=None,
                 runself=False, **kws):
        """ """
        self._enable_tray = enable_tray
        self._animate = animate
        self._conf_file = conf_file
        self._runself = runself
        # a right click context menu
        # not implemented for this release
        # normally menu is a xml based menu definition
        self.menu = None
        self._action_group = gtk.ActionGroup("Actions")
        self._uimanager = gtk.UIManager()

        self.main_ui = None
        self.icon_path = None

        if not self._enable_tray:
            self.toggle_main_ui()
            return

    def SetupMenu(self, menu_context, actions):
        """ """
        raise NotImplementedError
            
    def OnActivated(self, data=None):
        """ """
        self.toggle_main_ui()

    def OnQuit(self, widget=None):
        self.quit()

    def OnAbout(self, widget=None, data=None):
        self.main_ui.about_clicked(widget, data)

    def quit(self):
        """ """
        # since we didn't implemente menu, quit can only 
        # be done from the main UI window.
        raise NotImplementedError

    def toggle_main_ui(self):
        raise NotImplementedError

    def tray_clicked(self, widget, event):
        """ """
        raise NotImplementedError

    def SetIcon(self, file=None):
        raise NotImplementedError
    
    def SetTips(self, tips):
        raise NotImplementedError


class EggTrayIcon(TrayIcon):
    """
    """
    def __init__(self, **kws):
        """
        """
        super(EggTrayIcon, self).__init__(**kws)

        self.SetTips(tips)
        self.SetIcon(icon_file)
        self.trayIcon = egg.trayicon.TrayIcon("Crouke")

        self.eventBox.connect('button_press_event', self.tray_clicked)
        self.eventBox.add(self.icon)
        self.trayIcon.add(self.eventBox)
        self.trayIcon.show_all()

    # Override SetTips
    def SetTips(self, tips):
        self.eventBox = gtk.EventBox()
        self.tips = gtk.Tooltips()
        self.tips.set_tip(self.eventBox, tips)

    # Override SetIcon
    def SetIcon(self, file=None):
        if not self._enable_tray: return
        self.icon = gtk.Image()
        if file and os.path.exists(file) and os.access(file, os.R_OK):
            self.icon.set_from_file(file)

    # Override toggle_main_ui
    def toggle_main_ui(self):
        if not self.main_ui: 
            self.main_ui = croukeui.CroukeUI(self._conf_file, self._runself)
        if not self.main_ui.IsVisible():
            self.main_ui.show_window()
        else:
            return self.main_ui.close()

    # Override tray_clicked handler
    def tray_clicked(self, widget, event):
        # At this release, mouse key 1/3 all do the same thing.
        # If a menu is needed, we can implemente it in the future.
        if event.button == 1 or event.button == 3:
            self.toggle_main_ui()


class StatusTrayIcon(gtk.StatusIcon, TrayIcon):
    """
    """
    def __init__(self, **kws):
        super(StatusTrayIcon, self).__init__(**kws)
        gtk.StatusIcon.__init__(self)

        self.set_visible(True)
        self.connect('activate', self.OnActivated)
        self.SetTips(tips)
        self.SetIcon(icon_file)

    # Override SetTips
    def SetTips(self, tips):
        self.set_tooltip(tips)

    # Override SetIcon
    def SetIcon(self, file=None):
        if not self._enable_tray: return
        if file and os.path.exists(file) and os.access(file, os.R_OK):
            self.icon_path = file
            self.set_from_file(file)

    # Override toggle_main_ui
    def toggle_main_ui(self):
        if not self.main_ui: 
            self.main_ui = croukeui.CroukeUI(self._conf_file, self._runself)
        if not self.main_ui.IsVisible():
            self.main_ui.show_window()
        else:
            return self.main_ui.close()


class IconInfo(object):
    """
    """
    def __init__(self, icon):
        self._icon = icon

    # other methods to communicate with the backend through the icon


class CroukeIcon(object):
    """
    """
    def __init__(self, enable_tray=True, animate=True, icon_file=None,
                 tips=None, conf_file=None, runself=False, **kws):
        if USE_EGG:
            self.croukeTrayIcon = EggTrayIcon(enable_tray=enable_try,
                    animate=animate, icon_file=icon_file, tips=tips,
                    conf_file=conf_file, runself=runself, **kws)
        else:
            self.croukeTrayIcon = StatusTrayIcon(enable_tray=enable_tray,
                    animate=animate, icon_file=icon_file, tips=tips,
                    conf_file=conf_file, runself=runself, **kws)

        self.iconInfo = IconInfo(self.croukeTrayIcon)

    def main(self):
        gtk.main()


def main(argv):
    # main entry

    # postinst script installs the icon_file from settings.ICON_FILE
    # to /usr/share/pixmaps
    icon_file = '/usr/share/pixmaps/crouke.png'
    # OptionParse result feed into the parameter
    options, args = utils.ParseOptions(argv)
    if not options.enable_tray: runself = True
    if not options.conf_file: conf_file = settings.RC
    CroukeIcon(enable_tray=options.enable_tray, animate=options.animate,
        icon_file=icon_file, tips=_.tips, conf_file=conf_file,
        runself=runself).main()

if __name__ == '__main__':
    main(sys.argv)


