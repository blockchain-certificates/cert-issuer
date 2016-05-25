class Error(Exception):
    """Base class for exceptions in this module"""
    pass


class InsufficientFundsError(Error):
    pass


class UnrecognizedConnectorError(Error):
    pass


class ConnectorError(Error):
    pass


class UnverifiedSignatureError(Error):
    pass


class UnverifiedDocumentError(Error):
    pass

class NotImplementedError(Error):
    pass