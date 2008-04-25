#!/usr/bin/env python

"""Crouke's main UI. Providing a management interface for Crouke application.
Normally invoked by clicking the Crouke system tray icon.
"""

# system library
import gobject
import gtk
import gtk.glade
import pango
import os
import sys
import time

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

# Crouke modules
from backend import presentation
from config import settings
from config import texts as _
import utils


class CroukeUI(object):
    """The main Crouke application UI.
    
    Provide the main program interface and all children widgets.
    The UI is designed via glade3 and can be viewed and modified
    via crouke.glade file under ui subdirectory.
    """
    def __init__(self, conf_file=None, runself=True):
        """Constructor to init the UI object.
        
        Args:
            conf_file: the optional configuration file for Crouke.
                       Default is CROUKE_USER_SYS + croukerc
                       {@see config/settings.py}
            runself: optional whether or not the program is run
                     under standalone mode.
                     If you invoke this program directly, then
                     runself default is True, if you start
                     the Crouke tray icon, then the tray icon
                     invokes this main program by setting the
                     runself to False.
        """
        self._runself = runself
        self._conf_file = conf_file

        # Build the main UI window from glade
        self.gladefile = os.path.join(settings.UI_DIR, 'crouke.glade')
        self.wTree = gtk.glade.XML(self.gladefile)
        self.window = self.wTree.get_widget("top_window")

        # Connect the quit button to destroy.
        self.quit_butt = self.wTree.get_widget("quit_button")
        self.quit_butt.connect("clicked", self.destroy)

        # Connect about button to about method.
        self.wTree.get_widget("about_button").connect(
                "clicked", self.about_clicked)

        # Connect window destroy event to close
        # close will determine it should call destroy or just hide
        self.window.connect("destroy", self.close)
        
        # Same as delete_event
        self.window.connect("delete_event", self.close)

        # Set the visibility to False.
        self._visible = False
        
        # Run SilentLogin and get the result
        # If user/pass cached for user already, then this should
        # be successful, otherwise, login failure.
        # when user retrieves website contents, this result
        # will be checked against.
        self.login_result = self.SilentLogin()

        # If runself, then show the window
        if self._runself:
            self.show_window()

    def show_window(self):
        """Display the main program window.
        
        Also set the visible to True. When visible is True,
        the background update process will be paused.
        """
        self.window.show()
        if not self._visible: self._visible = True

    def SetVisible(self, visible):
        """Toggle visibility.
        
        Args:
            visible: boolean whether True/False.
        """
        self._visible = visible

    def IsVisible(self):
        """Check visibility of the window.
        
        Returns:
            boolean of the current visibility.
        """
        return self._visible
    
    def SilentLogin(self, username=None, password=None):
        """Perform silent login.
        
        Args:
            username: the username used to login.
            password: the password used to login.
        
        Returns:
            the login result. Either None indicates the login is successful,
            or gettext error string indicates the login has failed.
        """
        if not settings.SITES: settings.ParseRC(self._conf_file)
        self.client = presentation.Crouke(user=username,
                                          password=password)
        return self.client.ProgrammaticLogin()

    def DisplayError(self, err):
        """Popup the error dialog and return the response.
        
        Args:
            err: the error that will be shown.
        
        Returns:
            the gtk.RESPONSE_YES/NO.
        """
        # If silent login failed (most of the reasons would be:
        # 1. First time login
        # 2. username/password changed
        # 3. local caching file lost
        # 4. some other reason can't login using your username/password
        #    for example, network failure, website down, etc...
        # Except the first one and third (which all because there is nothing
        # cached locally), all other errors will be displayed to the end
        # user so that they can determine if they want to continue trying
        # login or not.
        # If there is no username/password cache found, the error is None.
        error_win = self._BuildErrorWindow()
        resp = error_win.run()
        error_win.destroy()
        return resp

    def PromptLogin(self):
        """Pop up a Login window."""
        self._BuildLoginWindow()
        self.login_win.run()
        login_win.hide()

    def _BuildErrorWindow(self, err=None):
        """Build an error dialog window.
        
        Args:
            err: the error that will be shown.
        
        Returns:
            the error dialog window widget.
        """
        error_dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_YES_NO,
                                         err)
        error_dialog.set_title(_.login_error)
        error_dialog.set_markup('<b>' + err + '</b>')
        return error_dialog

    def _BuildLoginWindow(self):
        """Build the Login window."""
        self.login_win = self.wTree.get_widget('login_dialog')
        self.login_win.connect('delete_event',
                               lambda x, y: self.login_win.hide())
        self.cancel_butt = self.wTree.get_widget('login_cancel_button')
        self.cancel_butt.connect('clicked', lambda x, y: self.login_win.hide())
        self.username_entry = self.wTree.get_widget('login_username_entry')
        self.password_entry = self.wTree.get_widget('login_password_entry')
        self.username_entry.connect('activate', self._OnOkLogin)
        self.password_entry.connect('activate', self._OnOkLogin)
        self.ok_butt = self.wTree.get_widget('login_ok_button')
        self.ok_butt.connect('clicked', self._OnOkLogin)
    
    def _OnOkLogin(self, widget=None, data=None):
        """Callback when the ok button is clicked in the Login window.
        
        When ok is clicked, it will perform a sanity check to see if
        username/password are all provided or not. Then it will call
        SilentLogin again to try login and then reset the login_result
        to whatever it gets.
        
        Args:
            widget: {@inherit}
            data: {@inherit}
        """
        username = self.username_entry.get_text().strip()
        password = self.password_entry.get_text().strip()
        if not username:
            mesg_dialog = gtk.MessageDialog(self.login_win, gtk.DIALOG_MODAL,
                              gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                              _.missing_username)
            mesg_dialog.set_markup('<b>' + _.missing_username + '</b>')
        elif not password:
            mesg_dialog = gtk.MessageDialog(self.login_win, gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_ERROR,
                                            gtk.BUTTONS_CLOSE,
                                            _.missing_password)
            mesg_dialog.set_markup('<b>' + _.missing_password + '</b>')
        else:
            mesg_dialog = gtk.MessageDialog(self.login_win, gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_ERROR,
                                            gtk.BUTTONS_CLOSE,
                                            _.missing_username_password)
            mesg_dialog.set_markup('<b>' + _.missing_username_password + '</b>')
        mesg_dialog.set_title(_.missing_entry_title)
        mesg_dialog.run()
        mesg_dialog.destroy()
        # when username/password are entered, run SilentLogin again
        # If login_result is None, then login successful.
        self.login_result = self.SilentLogin(user=username, password=password)
            
    def about_clicked(self, widget, data=None):
        about_dialog = self.wTree.get_widget("about_crouke")
        about_dialog.set_authors(["Yongjian (Jim) Xu"])
        about_dialog.run()
        about_dialog.hide()

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def close(self, widget=None, data=None):
        if self._runself:
            # TODO: get the current window size and remember it
            self.destroy()
        else:
            self.window.hide()
            self._visible = False
            self.SilentRun()
            return True

    def _SilentRun(self):
        # TODO: When Crouke is hide to a tray icon, kick off silent run
        # stuff will be updated in the background.
        while not self._visible:
            # do the actual updates
            while 
            pass


    def main(self):
        gtk.main()

if __name__ == '__main__':
    CroukeUI().main()

