"""Signs a Blockchain Certificate with the issuer's signing key.

This implementation signs the assertion uid, and populates the signature section.

After a Blockchain Certificate has been signed, it can be issed on the blockchain by using issue_certificates.py

"""
import json
import logging
import os

from cert_schema.schema_tools import schema_validator

from cert_issuer import helpers
from cert_issuer.errors import NoCertificatesFoundError, AlreadySignedError
from cert_issuer.secure_signing import Signer, FileSecretManager


def main(app_config):
    unsigned_certs_dir = app_config.unsigned_certificates_dir
    signed_certs_dir = app_config.signed_certificates_dir

    # find certificates to sign
    certificates = helpers.find_certificates_to_process(unsigned_certs_dir, signed_certs_dir)
    if not certificates:
        logging.warning('No certificates to process')
        raise NoCertificatesFoundError('No certificates to process')

    logging.info('Processing %d certificates', len(certificates))

    # create output dir if it doesn't exist
    os.makedirs(signed_certs_dir, exist_ok=True)

    # validate schema
    for uid, certificate in certificates.items():
        with open(certificate.unsigned_cert_file_name) as cert:
            cert_json = json.load(cert)
            schema_validator.validate_unsigned_v1_2(cert_json)

    # ensure they are not already signed. We want the user to know about this in case there
    # is a failure from a previous run
    for uid, certificate in certificates.items():
        with open(certificate.unsigned_cert_file_name) as cert:
            cert_json = json.load(cert)
            if 'signature' in cert_json and cert_json['signature']:
                logging.warning('Certificate with uid=%s has already been signed.', uid)
                raise AlreadySignedError('Certificate has already been signed')

    logging.info('Signing certificates and writing to folder %s', signed_certs_dir)
    path_to_secret = os.path.join(app_config.usb_name, app_config.key_file)
    signer = Signer(FileSecretManager(path_to_secret=path_to_secret, disable_safe_mode=app_config.safe_mode))
    signer.sign_certs(certificates)

    logging.info('Signed certificates are in folder %s', signed_certs_dir)


if __name__ == '__main__':
    from cert_issuer import config

    try:
        parsed_config = config.get_config()
        main(parsed_config)
    except Exception as ex:
        logging.error(ex, exc_info=True)
        exit(1)
