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


class UnableToSignTxError(Error):
    """
    The transaction could not be signed
    """
    pass


class UnverifiedTransactionError(Error):
    """
    The transaction could not be verified
    """
    pass


class AlreadySignedError(Error):
    """
    The certificate has already been signed
    """
    pass


class NoCertificatesFoundError(Error):
    """
    No certificates found
    """
    pass


class NonemptyOutputDirectoryError(Error):
    """
    The output directory is not empty
    """
    pass


class BroadcastError(Error):
    """
    Error broadcasting transaction
    """
    pass


class UnrecognizedChainError(Error):
    """
    Didn't recognize chain
    """
    pass
