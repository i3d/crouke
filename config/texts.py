import locale
import gettext
import settings


def translate():
    """Provide intl translation engine for Crouke.
    """
    # A nice tutorial found at:
    # http://www.learningpython.com/2006/12/03/translating-your-pythonpygtk-application/
    all_supported_langs = []
    lc, encoding = locale.getdefaultlocale()
    if lc: all_supported_langs.append(lc)
    other_langs = os.environ.get('LANGUAGE', None)
    if other_langs:
        all_supported_langs.extend(other_langs.split(':'))
    if 'en_US' not in all_supported_langs:
        all_supported_langs.append('en_US')

    engine = gettext.translation(settings.APP_NAME, settings.LANG_DIR,
                                 languages=all_supported_langs, fallback=True)
    _ = engine.gettext
    return _


_ = translate()



#################### All literal strings used in Crouke #####################
load_failed = _("Login Token failed to load. Please Login.")
auth_failed = _("Login authentication failure. Please relogin.")
sub_inst_failed = _("No sub directories contain valid theme file."
                    " Install can not proceed.")
inst_failed = _("Target directory does not contain a valid theme file."
                " Install can not proceed.")
unknown_file = _("Unknown file extension. Install can not proceed.")
tips = _("Starting Crouke ...")
login_error = _("Login Error")
missing_entry_title = _("Input Error")
missing_username = _("Username is required.")
missing_password = _("Password is required.")
missing_username_password = _("Username and password are required.")
#############################################################################
