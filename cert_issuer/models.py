import re
from abc import abstractmethod

from cert_issuer.config import ESTIMATE_NUM_INPUTS

def validate_type (certificate_type):
    compulsory_types = ['VerifiableCredential', 'VerifiablePresentation']
    if not isinstance(certificate_type, list):
        raise ValueError('`type` property should be an array')
    if isinstance(certificate_type, list) and len(certificate_type) <= 1:
        raise ValueError('`type` property should be an array with at least 2 values')
    if isinstance(certificate_type, list) and certificate_type[0] not in compulsory_types:
        raise ValueError('`type` property first value should be either VerifiableCredential or VerifiablePresentation')
    pass

def validate_credential_subject (credential_subject):
    pass

def validate_issuer (certificate_issuer):
    if not isinstance(certificate_issuer, str):
        raise ValueError('`issuer` property must be a string')
    pass

def validate_RFC3339_date (date):
    return re.match('^[1-9]\d{3}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}[Zz]$', date)

def validate_date_RFC3339_string_format (date, property_name):
    error_message = '{} property must be a valid RFC3339 string'.format(property_name)
    if not isinstance(date, str):
        raise ValueError(error_message)

    if not validate_RFC3339_date(date):
        raise ValueError(error_message)
    pass

def validate_issuance_date (certificate_issuance_date):
    validate_date_RFC3339_string_format(certificate_issuance_date, 'issuanceDate')
    pass

def validate_expiration_date (certificate_expiration_date):
    validate_date_RFC3339_string_format(certificate_expiration_date, 'expirationDate')
    pass

class BatchHandler(object):
    def __init__(self, secret_manager, certificate_handler, merkle_tree, config):
        self.certificate_handler = certificate_handler
        self.secret_manager = secret_manager
        self.merkle_tree = merkle_tree
        self.config = config

    @abstractmethod
    def pre_batch_actions(self, config):
        pass

    @abstractmethod
    def post_batch_actions(self, config):
        pass

    def set_certificates_in_batch(self, certificates_to_issue):
        self.certificates_to_issue = certificates_to_issue


class CertificateHandler(object):
    @abstractmethod
    def validate_certificate(self, certificate_metadata):
        validate_type(certificate_metadata['type'])

        try:
            # if undefined will throw KeyError
            validate_credential_subject(certificate_metadata['credentialSubject'])
        except:
            raise ValueError('`credentialSubject property must be defined`')

        try:
            # if undefined will throw KeyError
            validate_issuer(certificate_metadata['issuer'])
        except KeyError:
            raise ValueError('`issuer property must be defined`')
        except ValueError as err:
            raise ValueError(err)

        try:
            # if undefined will throw KeyError
            validate_issuance_date(certificate_metadata['issuanceDate'])
        except KeyError:
            raise ValueError('`issuance_date property must be defined`')
        except ValueError as err:
            raise ValueError(err)

        try:
            # if undefined will throw KeyError
            validate_expiration_date(certificate_metadata['expirationDate'])
        except KeyError:
            pass
        except ValueError as err:
            raise ValueError(err)

        pass

    @abstractmethod
    def sign_certificate(self, signer, certificate_metadata):
        pass

    @abstractmethod
    def get_byte_array_to_issue(self, certificate_metadata):
        pass

    @abstractmethod
    def add_proof(self, certificate_metadata, merkle_proof):
        pass


class ServiceProviderConnector(object):
    @abstractmethod
    def get_balance(self, address):
        pass

    def broadcast_tx(self, tx):
        pass


class Signer(object):
    """
    Abstraction for a component that can sign.
    """

    def __init__(self):
        pass

    @abstractmethod
    def sign_message(self, wif, message_to_sign):
        pass

    @abstractmethod
    def sign_transaction(self, wif, transaction_to_sign):
        pass


class SecretManager(object):
    def __init__(self, signer):
        self.signer = signer
        self.wif = None

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def sign_message(self, message_to_sign):
        return self.signer.sign_message(self.wif, message_to_sign)

    def sign_transaction(self, transaction_to_sign):
        return self.signer.sign_transaction(self.wif, transaction_to_sign)


class TransactionHandler(object):
    @abstractmethod
    def ensure_balance(self):
        pass

    @abstractmethod
    def issue_transaction(self, blockchain_bytes):
        pass


class MockTransactionHandler(TransactionHandler):
    def ensure_balance(self):
        pass

    def issue_transaction(self, op_return_bytes):
        return 'This has not been issued on a blockchain and is for testing only'


class TransactionCreator(object):
    @abstractmethod
    def estimate_cost_for_certificate_batch(self, tx_cost_constants, num_inputs=ESTIMATE_NUM_INPUTS):
        pass

    @abstractmethod
    def create_transaction(self, tx_cost_constants, issuing_address, inputs, op_return_value):
        pass
