import re
import logging
from urllib.parse import urlparse
from cert_schema import ContextUrls

# TODO: move the v3 checks to cert-schema
def validate_RFC3339_date (date):
    return re.match('^[1-9]\d{3}-\d{2}-\d{2}[Tt\s]\d{2}:\d{2}:\d{2}(?:\.\d{3})?((?:[+-]\d{2}:\d{2})|[Zz])$', date)

def is_valid_url (url):
    try:
        parsed_url = urlparse(url)
    except:
        return False
    return (not (parsed_url.path.__contains__(' ')
       or parsed_url.netloc.__contains__(' '))
       and url.__contains__(':'))

def validate_url (url):
    if not is_valid_url (url):
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
    ContextUrlsInstance = ContextUrls()
    vc_context_url = ContextUrlsInstance.verifiable_credential()
    blockcerts_valid_context_url = ContextUrlsInstance.v3_all()

    if not isinstance(context, list):
        raise ValueError('`@context` property must be an array')
    if context[0] != vc_context_url:
        raise ValueError('First @context declared must be {}, was given {}'.format(vc_context_url, context[0]))
    if len(type) > 1 and len(context) == 1:
        raise ValueError('A more specific type: {}, was detected, yet no context seems provided for that type'.format(type[1]))
    if context[-1] not in blockcerts_valid_context_url:
        logging.warning("""
           Last `@context` is not blockcerts' context. It is not a critical issue but some issues have come up at times
           because of some properties of a different context overwriting blockcerts' taxonomy. Check this property
           again in case of verification issue.
           """)

    pass

def validate_credential_subject (credential_subject):
    pass

def validate_issuer (certificate_issuer):
    has_error = False
    if isinstance(certificate_issuer, str) and not is_valid_url(certificate_issuer):
        has_error = True

    if isinstance(certificate_issuer, dict) and not is_valid_url(certificate_issuer['id']):
        has_error = True

    if isinstance(certificate_issuer, list):
        has_error = True
        
    if has_error:
        raise ValueError('`issuer` property must be a URL string or an object with an `id` property containing a URL string')
    pass

def validate_date_RFC3339_string_format (date, property_name):
    error_message = '`{}` property must be a valid RFC3339 string.'.format(property_name)
    if not isinstance(date, str):
        error_message += ' `{}` value is not a string'.format(date)
        raise ValueError(error_message)

    if not validate_RFC3339_date(date):
        error_message += ' Value received: `{}`'.format(date)
        raise ValueError(error_message)
    pass

def validate_issuance_date (certificate_issuance_date):
    validate_date_RFC3339_string_format(certificate_issuance_date, 'issuanceDate')
    pass

def validate_expiration_date (certificate_expiration_date):
    validate_date_RFC3339_string_format(certificate_expiration_date, 'expirationDate')
    pass

def validate_credential_status (certificate_credential_status):
    if not isinstance(certificate_credential_status, list):
        certificate_credential_status = [certificate_credential_status]

    for status in certificate_credential_status:
        try:
            validate_url(status['id'])
        except KeyError:
            raise ValueError('credentialStatus.id must be defined')
        except ValueError:
            raise ValueError('credentialStatus.id must be a valid URL')

        try:
            isinstance(status['type'], str)
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