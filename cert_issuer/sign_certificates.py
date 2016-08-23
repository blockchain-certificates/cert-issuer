"""
About:

Signs a certificate in accordance with the open badges spec.

It signs the assertion uid, and populates the signature section.

"""
import json
import logging
import time

import glob2
from bitcoin.signmessage import BitcoinMessage, SignMessage
from bitcoin.wallet import CBitcoinSecret
from cert_issuer import helpers
from cert_issuer.helpers import internet_off_for_scope
from cert_issuer.models import CertificateMetadata
from cert_schema.schema_tools import schema_validator


def find_unsigned_certificates(app_config):
    cert_info = {}
    for filename, (uid,) in glob2.iglob(
            app_config.unsigned_certs_file_pattern, with_matches=True):
        with open(filename) as cert_file:
            cert_raw = cert_file.read()
            cert_json = json.loads(cert_raw)
            certificate = CertificateMetadata(config=app_config,
                                              uid=uid,
                                              pubkey=cert_json['recipient']['pubkey'])
            cert_info[uid] = certificate

    return cert_info


@internet_off_for_scope
def sign_certs(certificates):
    """
    Sign certificates. Internet should be off for the scope of this function.
    :param certificates:
    :param allowable_wif_prefixes:
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

    logging.info('Processing %d certificates', len(certificates))

    # TODO
    for uid, certificate in certificates.items():
        schema_validator.validate_v1_2_0(certificate)

    # TODO:
    # - get revocation address per recipient revocation_address = app_config.revocation_address
    # - clean up previous signed certs

    start_time = str(time.time())

    logging.info('Signing certificates')
    sign_certs(certificates)

    logging.info('Archiving signed certificates.')
    helpers.archive_files(app_config.signed_certs_file_pattern,
                          app_config.archived_certs_file_pattern, start_time)


if __name__ == '__main__':
    from cert_issuer import config

    parsed_config = config.get_config()
    main(parsed_config)
