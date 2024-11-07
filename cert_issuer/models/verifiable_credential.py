import re
import logging
import json
from urllib.parse import urlparse
from cert_schema import ContextUrls
from urllib.request import urlretrieve
from jsonschema import validate as jsonschema_validate

# TODO: move the v3 checks to cert-schema
def validate_RFC3339_date (date):
    # // https://www.w3.org/TR/vc-data-model-2.0/#example-regular-expression-to-detect-a-valid-xml-schema-1-1-part-2-datetimestamp
    return re.match('-?([1-9][0-9]{3,}|0[0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))$', date)

def is_valid_url (url):
    try:
        parsed_url = urlparse(url)
    except:
        return False
    return (not (parsed_url.path.__contains__(' ')
       or parsed_url.netloc.__contains__(' '))
       and url.__contains__(':'))

def is_V1_verifiable_credential (context):
    ContextUrlsInstance = ContextUrls()
    return ContextUrlsInstance.verifiable_credential_v1() in context

def is_V2_verifiable_credential (context):
    ContextUrlsInstance = ContextUrls()
    return ContextUrlsInstance.verifiable_credential_v2() in context


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
    vc_context_url = [ContextUrlsInstance.verifiable_credential_v1(), ContextUrlsInstance.verifiable_credential_v2()]
    blockcerts_valid_context_url = ContextUrlsInstance.v3_all()

    if not isinstance(context, list):
        raise ValueError('`@context` property must be an array')
    if context[0] not in vc_context_url:
        raise ValueError('First @context declared must be one of {}, was given {}'.format(vc_context_url, context[0]))
    if is_V1_verifiable_credential(context) and is_V2_verifiable_credential(context):
        raise ValueError('Cannot have both v1 and v2 Verifiable Credentials contexts defined in the context array')
    if len(type) > 1 and len(context) == 1:
        raise ValueError('A more specific type: {}, was detected, yet no context seems provided for that type'.format(type[1]))
    if context[-1] not in blockcerts_valid_context_url:
        logging.warning("""
           Last `@context` is not blockcerts' context. It is not a critical issue but some issues have come up at times
           because of some properties of a different context overwriting blockcerts' taxonomy. Check this property
           again in case of verification issue.
           """)

    pass

def validate_credential_subject (credential_subject, credential_schema):
    if not isinstance(credential_schema, list):
        credential_schema = [credential_schema]

    if not isinstance(credential_subject, list):
        credential_subject = [credential_subject]

    for schema in credential_schema:
        schema_url = schema['id']
        local_filename, headers = urlretrieve(schema_url)
        with open(local_filename) as f:
            schema = json.load(f)
            for subject in credential_subject:
                jsonschema_validate(subject, schema)
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

def validate_valid_from_date (certificate_valid_from_date):
    validate_date_RFC3339_string_format(certificate_valid_from_date, 'validFrom')
    pass

def validate_valid_until_date (certificate_valid_until_date):
    validate_date_RFC3339_string_format(certificate_valid_until_date, 'validUntil')
    pass

def validate_date_set_after_other_date(second_date, first_date, second_date_key, first_date_key):
    if not second_date > first_date:
        raise ValueError('`{}` property must be a date set after `{}`'.format(second_date_key, first_date_key))
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

def validate_credential_schema (certificate_credential_schema):
    if not isinstance(certificate_credential_schema, list):
        certificate_credential_schema = [certificate_credential_schema]

    for schema in certificate_credential_schema:
        try:
            validate_url(schema['id'])
        except KeyError:
            raise ValueError('credentialSchema.id must be defined')
        except ValueError:
            raise ValueError('credentialSchema.id must be a valid URL')

        try:
            isinstance(schema['type'], str)
            if (schema['type'] != 'JsonSchema'):
                raise ValueError('Value of credentialSchema.type must be JsonSchema')
        except KeyError:
            raise ValueError('credentialSchema.type must be defined')
        except:
            raise ValueError('credentialSchema.type must be a string of value: JsonSchema', schema['id'])
    pass

def verify_credential(certificate_metadata):
    try:
        # if undefined will throw KeyError
        credential_subject = certificate_metadata['credentialSubject']
    except:
        raise ValueError('`credentialSubject` property must be defined')

    try:
        # if undefined will throw KeyError
        validate_issuer(certificate_metadata['issuer'])
    except KeyError:
        raise ValueError('`issuer` property must be defined')
    except ValueError as err:
        raise ValueError(err)

    if is_V1_verifiable_credential(certificate_metadata['@context']):
        try:
            # if undefined will throw KeyError
            validate_issuance_date(certificate_metadata['issuanceDate'])
        except KeyError:
            raise ValueError('`issuanceDate` property must be defined')
        except ValueError as err:
            raise ValueError(err)

        if 'expirationDate' in certificate_metadata:
            try:
                # if undefined will throw KeyError
                validate_expiration_date(certificate_metadata['expirationDate'])
                validate_date_set_after_other_date(
                    certificate_metadata['expirationDate'],
                    certificate_metadata['issuanceDate'],
                    'expirationDate',
                    'issuanceDate'
                )
            except KeyError:
                # optional property
                pass
            except ValueError as err:
                raise ValueError(err)

    if is_V2_verifiable_credential(certificate_metadata['@context']):
        try:
            # if undefined will throw KeyError
            validate_valid_from_date(certificate_metadata['validFrom'])
        except KeyError:
            # optional property
            pass
        except ValueError as err:
            raise ValueError(err)

        if 'validUntil' in certificate_metadata:
            try:
                # if undefined will throw KeyError
                validate_valid_until_date(certificate_metadata['validUntil'])
                if 'validFrom' in certificate_metadata:
                    validate_date_set_after_other_date(
                        certificate_metadata['validUntil'],
                        certificate_metadata['validFrom'],
                        'validUntil',
                        'validFrom'
                    )
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

    try:
        # if undefined will throw KeyError
        credential_schema = certificate_metadata['credentialSchema']
        validate_credential_schema(credential_schema)
        validate_credential_subject(credential_subject, credential_schema)
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