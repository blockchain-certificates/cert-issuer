import re
from urllib.parse import urlparse
from abc import abstractmethod

from cert_issuer.config import ESTIMATE_NUM_INPUTS

def validate_RFC3339_date (date):
    return re.match('^[1-9]\d{3}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}[Zz]$', date)

def is_valid_url (url):
    try:
        parsed_url = urlparse(url)
    except:
        return False
    return (not (parsed_url.path.__contains__(' ')
       or parsed_url.netloc.__contains__(' '))
       and url.__contains__(':'))

def validate_url (url):
    if not is_valid_url (parsed_url):
        raise ValueError('Invalid URL: {}'.format(url))
    pass

def validate_type (certificate_type):
    compulsory_types = ['VerifiableCredential', 'VerifiablePresentation']
    if not isinstance(certificate_type, list):
        raise ValueError('`type` property must be an array')

    contains_compulsory_types = list(set(compulsory_types) & set(certificate_type))
    if len(certificate_type) == 0 or len(contains_compulsory_types) == 0:
        raise ValueError('`type` property must be an array with at least `VerifiableCredential` or `VerifiablePresentation` value')
    pass

def validate_context (context, type):
    vc_context_url = 'https://www.w3.org/2018/credentials/v1'

    if not isinstance(context, list):
        raise ValueError('`@context` property must be an array')
    if context[0] != vc_context_url:
        raise ValueError('First @context declared must be {}, was given {}'.format(vc_context_url, context[0]))
    if len(type) > 1 and len(context) == 1:
        raise ValueError('A more specific type: {}, was detected, yet no context seems provided for that type'.format(type[1]))

    pass

def validate_credential_subject (credential_subject):
    pass

def validate_issuer (certificate_issuer):
    if not is_valid_url(certificate_issuer) and not is_valid_url(certificate_issuer['id']):
        raise ValueError('`issuer` property must be a URL string or an object with an `id` property containing a URL string')
    pass

def validate_date_RFC3339_string_format (date, property_name):
    error_message = '`{}` property must be a valid RFC3339 string'.format(property_name)
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

def validate_credential_status (certificate_credential_status):
    try:
        validate_url(certificate_credential_status['id'])
    except KeyError:
        raise ValueError('credentialStatus.id must be defined')
    except ValueError:
        raise ValueError('credentialStatus.id must be a valid URL')

    try:
        isinstance(certificate_credential_status['type'], str)
    except KeyError:
        raise ValueError('credentialStatus.type must be defined')
    except:
        raise ValueError('credentialStatus.type must be a string')
    pass

def verify_credential(certificate_metadata):
    try:
        # if undefined will throw KeyError
        validate_credential_subject(certificate_metadata['credentialSubject'])
    except:
        raise ValueError('`credentialSubject` property must be defined')

    try:
        # if undefined will throw KeyError
        validate_issuer(certificate_metadata['issuer'])
    except KeyError:
        raise ValueError('`issuer` property must be defined')
    except ValueError as err:
        raise ValueError(err)

    try:
        # if undefined will throw KeyError
        validate_issuance_date(certificate_metadata['issuanceDate'])
    except KeyError:
        raise ValueError('`issuanceDate` property must be defined')
    except ValueError as err:
        raise ValueError(err)

    try:
        # if undefined will throw KeyError
        validate_expiration_date(certificate_metadata['expirationDate'])
    except KeyError:
        # optional property
        pass
    except ValueError as err:
        raise ValueError(err)

    try:
        # if undefined will throw KeyError
        validate_credential_status(certificate_metadata['credentialStatus'])
    except KeyError:
        # optional property
        pass
    except ValueError as err:
        raise ValueError(err)

    pass

def verify_presentation (certificate_metadata):
    try:
        for credential in certificate_metadata['verifiableCredential']:
            verify_credential(credential)
    except:
        raise ValueError('A Verifiable Presentation must contain valid verifiableCredential(s)')
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
        validate_context(certificate_metadata['@context'], certificate_metadata['type'])

        if (certificate_metadata['type'][0] == 'VerifiableCredential'):
            verify_credential(certificate_metadata)

        if (certificate_metadata['type'][0] == 'VerifiablePresentation'):
            verify_presentation(certificate_metadata)

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
