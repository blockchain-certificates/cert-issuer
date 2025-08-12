import re
import logging
import json
from urllib.parse import urlparse
from cert_schema import ContextUrls
from urllib.request import urlretrieve
from jsonschema import validate as jsonschema_validate
from dateutil import parser, tz
from cert_issuer.digests import validate_digest_sri, validate_digest_multibase

# TODO: move the v3 checks to cert-schema
def validate_RFC3339_date(date):
    # // https://www.w3.org/TR/vc-data-model-2.0/#example-regular-expression-to-detect-a-valid-xml-schema-1-1-part-2-datetimestamp
    return re.match('-?([1-9][0-9]{3,}|0[0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))$', date)


def is_valid_url(url):
    try:
        parsed_url = urlparse(url)
    except:
        return False
    return (not (parsed_url.path.__contains__(' ')
       or parsed_url.netloc.__contains__(' '))
       and url.__contains__(':'))


def is_V1_verifiable_credential(context):
    ContextUrlsInstance = ContextUrls()
    return ContextUrlsInstance.verifiable_credential_v1() in context


def is_V2_verifiable_credential(context):
    ContextUrlsInstance = ContextUrls()
    return ContextUrlsInstance.verifiable_credential_v2() in context


def validate_url(url):
    if not is_valid_url(url):
        raise ValueError('Invalid URL: {}'.format(url))
    pass


def validate_type(certificate_type):
    compulsory_types = ['VerifiableCredential', 'VerifiablePresentation']
    if not isinstance(certificate_type, list):
        raise ValueError('`type` property must be an array')

    contains_compulsory_types = list(set(compulsory_types) & set(certificate_type))
    if len(certificate_type) == 0 or len(contains_compulsory_types) == 0:
        raise ValueError('`type` property must be an array with at least `VerifiableCredential` or `VerifiablePresentation` value')
    pass


def validate_id(identifier):
    if not isinstance(identifier, str):
        raise TypeError('"@id" value must be a string.')
    validate_url(identifier)
    pass


def validate_context(context, type):
    ContextUrlsInstance = ContextUrls()
    vc_context_url = [ContextUrlsInstance.verifiable_credential_v1(), ContextUrlsInstance.verifiable_credential_v2()]
    blockcerts_valid_context_url = ContextUrlsInstance.v3_all()

    if not isinstance(context, list):
        raise ValueError('`@context` property must be an array')
    if len(context) == 0:
        raise ValueError('`@context` array cannot be empty')
    if context[0] not in vc_context_url:
        raise ValueError('First @context declared must be one of {}, was given {}'.format(vc_context_url, context[0]))
    if is_V1_verifiable_credential(context) and is_V2_verifiable_credential(context):
        raise ValueError('Cannot have both v1 and v2 Verifiable Credentials contexts defined in the context array')
    if is_V1_verifiable_credential(context) and len(type) > 1 and len(context) == 1:
        raise ValueError('A more specific type: {}, was detected, yet no context seems provided for that type'.format(type[1]))
    if context[-1] not in blockcerts_valid_context_url:
        logging.warning("""
           Last `@context` is not blockcerts' context. It is not a critical issue but some issues have come up at times
           because of some properties of a different context overwriting blockcerts' taxonomy. Check this property
           again in case of verification issue.
           """)

    pass


def validate_credential_subject(credential_subject):
    if not isinstance(credential_subject, list):
        credential_subject = [credential_subject]

    for subject in credential_subject:
        if not isinstance(subject, dict) or not subject:
            raise ValueError('`credentialSubject` must be a non empty object')


def validate_credential_subject_against_schema(credential_subject, credential_schema):
    if not isinstance(credential_schema, list):
        credential_schema = [credential_schema]

    if not isinstance(credential_subject, list):
        credential_subject = [credential_subject]

    for schema in credential_schema:
        schema_url = schema['id']
        local_filename, headers = urlretrieve(schema_url)
        with open(local_filename) as f:
            schema_data = json.load(f)
            for subject in credential_subject:
                jsonschema_validate(subject, schema_data)


def validate_issuer(certificate_issuer):
    has_error = False
    if certificate_issuer is None:
        has_error = True

    if isinstance(certificate_issuer, str) and not is_valid_url(certificate_issuer):
        has_error = True

    if isinstance(certificate_issuer, dict):
        if certificate_issuer['id'] is None:
            has_error = True
        if certificate_issuer['id'] is not None and not is_valid_url(certificate_issuer['id']):
            has_error = True

    if isinstance(certificate_issuer, list):
        has_error = True
        
    if has_error:
        raise ValueError('`issuer` property must be a URL string or an object with an `id` property containing a URL string')
    pass


def validate_date_RFC3339_string_format(date, property_name):
    error_message = '`{}` property must be a valid RFC3339 string.'.format(property_name)
    if not isinstance(date, str):
        error_message += ' `{}` value is not a string'.format(date)
        raise ValueError(error_message)

    if not validate_RFC3339_date(date):
        error_message += ' Value received: `{}`'.format(date)
        raise ValueError(error_message)
    pass


def validate_issuance_date(certificate_issuance_date):
    validate_date_RFC3339_string_format(certificate_issuance_date, 'issuanceDate')
    pass


def validate_expiration_date(certificate_expiration_date):
    validate_date_RFC3339_string_format(certificate_expiration_date, 'expirationDate')
    pass


def validate_valid_from_date(certificate_valid_from_date):
    validate_date_RFC3339_string_format(certificate_valid_from_date, 'validFrom')
    pass


def validate_valid_until_date(certificate_valid_until_date):
    validate_date_RFC3339_string_format(certificate_valid_until_date, 'validUntil')
    pass


def validate_date_set_after_other_date(second_date_str, first_date_str, second_date_key, first_date_key):
    first_date = parser.isoparse(first_date_str)
    second_date = parser.isoparse(second_date_str)

    # Ensure both are in UTC
    first_date = first_date.astimezone(tz=None).astimezone(tz=tz.UTC)
    second_date = second_date.astimezone(tz=None).astimezone(tz=tz.UTC)

    if not second_date > first_date:
        raise ValueError('`{}` property must be a date set after `{}`'.format(second_date_key, first_date_key))
    pass


def validate_related_resource(related_resource):
    logging.info('A relatedResource object was passed, validating...')
    if not isinstance(related_resource, list):
        related_resource = [related_resource]

    if any(not isinstance(resource, dict) for resource in related_resource):
        raise ValueError('relatedResource entry must be an object')

    for resource in related_resource:
        if 'id' not in resource:
            raise ValueError('relatedResource.id is required')
        else:
            logging.info('relatedResource.id is specified')
            try:
                validate_url(resource['id'])
            except ValueError:
                raise ValueError('relatedResource.id must be a valid URL')
            logging.info('relatedResource.id is a valid URL')

        if 'digestSRI' not in resource and 'digestMultibase' not in resource:
            raise ValueError('a relatedResource must contain at least a digestSRI or a digestMultibase')

        if 'digestSRI' in resource:
            logging.info('A digest SRI was specified, validating...')
            try:
                validate_digest_sri(resource['id'], resource['digestSRI'])
            except ValueError as err:
                raise ValueError(err)

        if 'digestMultibase' in resource:
            logging.info('A digest multibase was specified, validating...')
            try:
                validate_digest_multibase(resource['id'], resource['digestMultibase'])
            except ValueError as err:
                raise ValueError(err)



    if len({resource['id'] for resource in related_resource}) != len(related_resource):
        raise ValueError('Each "id" in relatedResource must be unique')


def validate_prop_type_and_id(prop, prop_name):
    if not isinstance(prop, list):
        prop = [prop]

    for p in prop:
        if 'id' not in p:
            if prop_name == 'credentialSchema':
                raise ValueError('{}.id must be defined'.format(prop_name))
            # else optional
        else:
            try:
                validate_url(p['id'])
            except ValueError:
                raise ValueError('{}.id must be a valid URL'.format(prop_name))

        try:
            isinstance(p['type'], str)
        except KeyError:
            raise ValueError('{}.type must be defined'.format(prop_name))
        except:
            raise ValueError('{}.type must be a string'.format(prop_name))
    pass


def validate_data_integrity_proof(proof):
    required_keys = [
        'type',
        'created',
        'verificationMethod',
        'proofPurpose',
        'proofValue'
    ]
    proof_type = proof['type']
    for key in required_keys:
        if key not in proof:
            raise ValueError(f'Missing required key: `{key}` in Data Integrity proof')

    if proof_type == 'DataIntegrityProof':
        if 'cryptosuite' not in proof:
            raise ValueError(f'Missing required key: `cryptosuite` in Data Integrity proof')

    validate_date_RFC3339_string_format(proof['created'], 'proof.created')

    if 'expires' in proof:
        validate_date_RFC3339_string_format(proof['expires'], 'proof.expires')

    pass


def validate_proof_format(proof):
    if not isinstance(proof, list):
        proof = [proof]

    for p in proof:
        if 'type' not in p:
            raise ValueError('proof.type must be defined')

        validate_data_integrity_proof(p)

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

    try:
        validate_id(certificate_metadata['id'])
    except KeyError:
        pass  # optional property
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
        logging.info('Validating a VC v2 credential')
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
        validate_credential_subject(credential_subject)
    except ValueError as err:
        raise ValueError(err)

    # individually handle optional properties
    for key in ['credentialStatus', 'evidence', 'refreshService', 'termsOfUse']:
        try:
            validate_prop_type_and_id(certificate_metadata[key], key)
        except KeyError:
            pass  # property is optional
        except ValueError as err:
            raise ValueError(err)

    try:
        validate_related_resource(certificate_metadata['relatedResource'])
    except KeyError:
        pass  # optional property
    except ValueError as err:
        raise ValueError(err)

    try:
        credential_schema = certificate_metadata['credentialSchema']
        validate_prop_type_and_id(credential_schema, 'credentialSchema')
        validate_credential_subject_against_schema(credential_subject, credential_schema)
    except KeyError:
        pass  # credentialSchema is optional
    except ValueError as err:
        raise ValueError(err)

    pass


def verify_presentation(certificate_metadata):
    try:
        for credential in certificate_metadata['verifiableCredential']:
            if credential['type'] != 'EnvelopedVerifiableCredential':
                if 'proof' not in credential:
                    raise ValueError('Each Verifiable Credential in a Verifiable Presentation must be signed')

                validate_proof_format(credential['proof'])

            verify_credential(credential)
    except ValueError as err:
        raise ValueError(f'A Verifiable Presentation must contain valid verifiableCredential(s): {err}')
    pass