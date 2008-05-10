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
        # a stack to store the views
        self._remote_stack = { 'main': None,
                               'kde-apps': [],
                               'qt_apps': [],
                               'eyeos_apps': [],
                               'java_apps': [],
                               'maemo_apps': [],
                               'qt_prog': [],
                               'cli_apps': [],
                               'gtk_apps': [],
                               'android': [],
                               'ubuntu_art': [],
                               'suse_art': [],
                               'kubuntu_art': [],
                               'gentoo_art': [],
                               'debian_art': [],
                               'kde_files': [],
                               'gnome_look': [],
                               'kde_look': [],
                               'xfce_look': [],
                               'e17_stuff': [],
                               'opentemplate': [],
                               'opendesktop': [],
                               'box_look': [],
                               'beryl_themes': [],
                               'compiz': [],
                            }


        self._local_stack = []
        
        # pos used as stack pointer and also the current web page
        # initial is -2, pointing to None.
        # The first website list UI is -1.
        # Any website going into will start with 0.
        
        # Actual index number in stack equals to pos number + 1.
        # e.g. website icons list in stack will be indexed 0 with
        # pos number -1. If user goes to www.gnome-look.org, then
        # the second UI stored in stack would be 1 and pos 0 (which is
        # at web page 0).
        self._pos = -2
        
        # on remote view or local view
        self._on_remote = True

        self._runself = runself
        self._conf_file = conf_file

        # Build the main UI window from glade
        self.gladefile = os.path.join(settings.UI_DIR, 'crouke.glade')
        self.wTree = gtk.glade.XML(self.gladefile)
        self.window = self.wTree.get_widget("top_window")

        # Connect window destroy event to close
        # close will determine it should call destroy or just hide
        self.window.connect("destroy", self.close)
        
        # Same as delete_event
        self.window.connect("delete_event", self.close)

        # Set the visibility to False.
        self._visible = False

        # Get the main container object and push its child to the queue.
        # The main container is a ScrollWindow container and always only
        # has one child.
        # The first window always the sites in the container.
        # Later on when user cruise the sites, the container will
        # offload/upload its child back and forth.
        self._main_container = self.wTree.get_widget("main_container")
        self._remote_stack.append(self._main_container.child)
        
        # the api client
        self._client = None

        # Preference window
        self.pref_window = self.wTree.get_widget("pref_button")
        
        # Status bar
        self.status_bar = self.wTree.get_widget("buttom_statusbar")
        
        # Run SilentLogin and get the result
        # If user/pass cached for user already, then this should
        # be successful, otherwise, login failure.
        # when user retrieves website contents, this result
        # will be checked against.
        self.login_result = self.SilentLogin()
        if not self.login_result:
            self.status_bar.set_text(_.login_successful)

        # Connect all buttons to their callbacks
        connections = {'on_remote_clicked' : self.GoRemote,
                       'on_local_clicked' : self.GoLocal,
                       'on_pref_clicked' : self.GoPref,
                       'on_about_clicked' : self.GoAbout,
                       'on_quit_clicked' : self.destroy,
                       'on_login_clicked' : self.PromptLogin,
                       'on_logout_clicked' : self.Logout,
                       'on_back_clicked' : self.GoBack,
                       'on_forward_clicked' : self.GoForward,
                       'on_refresh_clicked' : self.GoRefresh,
                       'on_home_clicked' : self.GoHome,
                       'on_find_clicked' : self.GoFind,
                       'on_kde_apps_clicked' : self.GoKdeApps,
                       'on_qt_apps_clicked' : self.GoQtApps,
                       'on_eyeos_apps_clicked' : self.GoEyeosApps,
                       'on_java_apps_clicked' : self.GoJavaApps,
                       'on_maemo_apps_clicked' : self.GoMaemoApps,
                       'on_qt_prog_clicked' : self.GoQtProg,
                       'on_cli_apps_clicked' : self.GoCliApps,
                       'on_gtk_apps_clicked' : self.GoGtkApps,
                       'on_android_clicked' : self.GoAndroid,
                       'on_ubuntu_art_clicked' : self.GoUbuntuArt,
                       'on_suse_art_clicked' : self.GoSuseArt,
                       'on_kubuntu_art_clicked' : self.GoKubuntuArt,
                       'on_gentoo_art_clicked' : self.GoGentooArt,
                       'on_debian_art_clicked' : self.GoDebianArt,
                       'on_kde_files_clicked' : self.GoKdeFiles,
                       'on_gnome_look_clicked' : self.GoGnomeLook,
                       'on_kde_look_clicked' : self.GoKdeLook,
                       'on_xfce_look_clicked' : self.GoXfceLook,
                       'on_e17_stuff_clicked' : self.GoE17Stuff,
                       'on_opentemplate_clicked' : self.GoOpenTemplate,
                       'on_opendesktop_clicked' : self.GoOpenDesktop,
                       'on_box_look_clicked' : self.GoBoxlook,
                       'on_beryl_themes_clicked' : self.GoBerylThemes,
                       'on_compiz_clicked' : self.GoCompiz,}

        self.wTree.signal_autoconnect(connections)

        # If runself, then show the window
        if self._runself:
            self.show_window()

    def show_window(self):
        """Display the main program window.
        
        Also set the visible to True. When visible is True,
        the background update process will be paused.
        """
        self.status_bar.set_text(_.loading)
        self.window.show()
        if not self._visible: self._visible = True
        self.status_bar.set_text(_.done)

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
        self.status_bar.set_text(_.perform_login)
        if not settings.SITES: settings.ParseRC(self._conf_file)
        if not self._client:
            self._client = presentation.Crouke(user=username,
                                               password=password)
        else:
            self._client.SetUser(username)
            self._client.SetPassword(password)
        return self._client.ProgrammaticLogin()

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
        self.status_bar.set_text(_.perform_login)
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
            
    def destroy(self, widget, data=None):
        """Self destroy the UI and quit the application.
        """
        gtk.main_quit()

    def close(self, widget=None, data=None):
        """A frendent to destroy.

        Called from tray if the app is started as a tray. Since normally,
        tray is just minimized instead of closed.
        """
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
        
        

    
    ####################################################################
    #                                                                  #
    # Customized widgets
    #                                                                  #
    ####################################################################



    ####################################################################
    #                                                                  #
    # Callback handlers for the first UI.                              #
    #                                                                  #
    ####################################################################

    def PromptLogin(self):
        """Pop up a Login window."""
        self._BuildLoginWindow()
        self.login_win.run()
        if not self.login_result:
            self.status_bar.set_text(_.login_successful)
        else:
            self.status_bar.set_text(_.login_failed)        
        login_win.hide()

    def GoAbout(self, widget, data=None):
        """Callback for About button click"""
        about_dialog = self.wTree.get_widget("about_crouke")
        about_dialog.set_authors(["Yongjian (Jim) Xu"])
        about_dialog.run()
        about_dialog.hide()
    
    def GoRemote(self, widget=None, data=None):
        """Callback for Remote button click"""
        if not self._on_remote:
            self._on_remote = True
            if self._remote_stack and self._pos > -2:
                obj = self._remote_stack[self._pos + 1]
                self._main_container.child_set(obj)
                self._main_container.set_child_visible(True)
    
    def GoLocal(self, widget=None, data=None):
        """Callback for Local button click"""
        if self._on_remote:
            self._on_remote = False
            if self._local_stack:
                obj = self._local_stack.pop()
            else:
                # TODO (jimxu): build the local filesystem view
                # store it into the local stack
            self._main_container.child_set(obj)
            self._main_container.set_child_visible(True)
    
    def GoPref(self, widget=None, data=None):
        """Callback for Preference button click
       
        Note: Preference is the UI to manipulate  
        """
        pass

    def Logout(self, widget=None, data=None):
        """Reset the user/password"""
        if self._client:
            self._client.Logout()
        self.status_bar.set_text(_.logged_out)
    
    def GoBack(self, widget=None, data=None):
        """Retrieve the previous page"""
        if self._on_remote and self._pos > -1:
            previous = self._remote_stack[self._pos]
            self._pos -= 1
            if self._main_container.child not in self._remote_stack:
                self._remote_stack.append(self._main_container.child)
            self._main_container.child_set(previous)
            self._main_container.set_child_visible(True)
    
    def GoForward(self, widget=None, data=None):
        """Go to the next page"""
        if self._on_remote:
            if self._pos == len(self._remote_stack) - 1:
                # TODO (jimxu): Create new page.
                if self._pos = -1:
                    # one the first page, hasn't pick which website yet
                    # so can't go forward
                    # TODO (jimxu): display a warning
                else:
                    # site was picked, just go to the next page.
            else:
                self._pos += 1
                page = self._remote_stack[self._pos + 1]
            
            self._main_container.child_set(page)
            self._main_container.set_child_visible(True)
            
                

if __name__ == '__main__':
    CroukeUI().main()

