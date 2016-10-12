class Error(Exception):
    """Base class for exceptions in this module"""
    pass


class InsufficientFundsError(Error):
    """
    There are insufficient funds to issue certificates
    """
    pass


class ConnectorError(Error):
    pass


class UnverifiedSignatureError(Error):
    """
    The signature in the certificate does not match the issuer's address
    """
    pass


class UnverifiedTransactionError(Error):
    """
    The transaction could not be verified
    """
    pass
