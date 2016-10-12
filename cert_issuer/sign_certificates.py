"""Signs a Blockchain Certificate with the issuer's signing key.

This implementation signs the assertion uid, and populates the signature section.

After a Blockchain Certificate has been signed, it can be issed on the blockchain by using issue_certificates.py

"""
import collections
import json
import logging

import glob2
from bitcoin.signmessage import BitcoinMessage, SignMessage
from bitcoin.wallet import CBitcoinSecret
from cert_schema.schema_tools import schema_validator

from cert_issuer import helpers
from cert_issuer.helpers import internet_off_for_scope
from cert_issuer.models import CertificateMetadata


def find_unsigned_certificates(app_config):
    cert_info = collections.OrderedDict()
    for filename, (uid,) in sorted(glob2.iglob(
            app_config.unsigned_certs_file_pattern, with_matches=True)):
        with open(filename) as cert_file:
            cert_raw = cert_file.read()
            cert_json = json.loads(cert_raw)
            certificate = CertificateMetadata(config=app_config,
                                              uid=uid,
                                              public_key=cert_json['recipient']['publicKey'])
            cert_info[uid] = certificate

    return cert_info


@internet_off_for_scope
def sign_certs(certificates):
    """
    Sign certificates. Internet should be off for the scope of this function.
    :param certificates:
    :return:
    """
    logging.info('signing certificates')
    pk = helpers.import_key()
    secret_key = CBitcoinSecret(pk)
    for uid, certificate in certificates.items():
        with open(certificate.unsigned_certificate_file_name, 'r') as cert_in, \
                open(certificate.signed_certificate_file_name, 'wb') as signed_cert:
            cert = _sign(cert_in.read(), secret_key)
            signed_cert.write(bytes(cert, 'utf-8'))


def _sign(certificate, secret_key):
    """
    Signs the certificate.
    :param certificate:
    :param secret_key:
    :return:
    """
    cert = json.loads(certificate)
    to_sign = cert['assertion']['uid']
    message = BitcoinMessage(to_sign)
    signature = SignMessage(secret_key, message)
    cert['signature'] = str(signature, 'utf-8')
    sorted_cert = json.dumps(cert, sort_keys=True)
    return sorted_cert


def main(app_config):
    # find certificates to process
    certificates = find_unsigned_certificates(app_config)
    if not certificates:
        logging.info('No certificates to process')
        exit(0)

    batch_id = helpers.get_batch_id(list(certificates.keys()))
    logging.info('Processing %d certificates with batch id=%s', len(certificates), batch_id)

    # validate schema
    for uid, certificate in certificates.items():
        with open(certificate.unsigned_certificate_file_name) as cert:
            cert_json = json.load(cert)
            schema_validator.validate_unsigned_v1_2(cert_json)

    # ensure they are not already signed. We want the user to know about this in case there
    # is a failure from a previous run
    for uid, certificate in certificates.items():
        with open(certificate.unsigned_certificate_file_name) as cert:
            cert_json = json.load(cert)
            if 'signature' in cert_json and cert_json['signature']:
                logging.warning('Certificate with uid=%s has already been signed.', uid)
                exit(0)

    logging.info('Signing certificates and writing to folder %s', app_config.signed_certs_file_pattern)
    sign_certs(certificates)

    logging.info('Archiving unsigned files to archive folder %s', batch_id)
    helpers.archive_files(app_config.unsigned_certs_file_pattern,
                          app_config.archive_path,
                          app_config.unsigned_certs_file_part,
                          batch_id)


if __name__ == '__main__':
    from cert_issuer import config

    parsed_config = config.get_config()
    main(parsed_config)
