# Generic Error exception.
class Error(Exception):
    pass

# Exception raised during installation.
class InstallError(Error):
    pass

# Exception raised when can't read Login token.
class LoadLoginTokenError(Error):
    pass

# Exception raised when can't write Login token.
class SaveLoginTokenError(Error):
    pass

# Exception raised when Request/Response handling error.
class RequestHandlingError(Error):
    pass
