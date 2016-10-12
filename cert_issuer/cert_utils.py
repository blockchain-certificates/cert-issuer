"""
Helpers for certificates
"""

import json
import logging

from bitcoin.signmessage import BitcoinMessage
from bitcoin.signmessage import VerifyMessage

from cert_issuer.errors import UnverifiedDocumentError, UnverifiedSignatureError


def verify_signature(uid, signed_certificate_file_name, issuing_address):
    """
    Verify the certificate signature matches the expected. Double-check the uid field in the certificate and use
    VerifyMessage to confirm that the signature in the certificate matches the issuing_address
    :param uid:
    :param signed_certificate_file_name:
    :param issuing_address:
    :return:
    """

    # Throws an error if invalid
    logging.info('verifying signature for certificate with uid=%s:', uid)
    with open(signed_certificate_file_name) as in_file:
        signed_cert = in_file.read()
        signed_cert_json = json.loads(signed_cert)

        to_verify = signed_cert_json['assertion']['uid']
        signature = signed_cert_json['signature']
        message = BitcoinMessage(to_verify)
        verified = VerifyMessage(issuing_address, message, signature)
        if not verified:
            error_message = 'There was a problem with the signature for certificate uid={}'.format(
                signed_cert_json['assertion']['uid'])
            raise UnverifiedSignatureError(error_message)

        logging.info('verified signature')


def verify_transaction(op_return_value, signed_hextx):
    """
    Verify the signed transaction. Ensure OP_RETURN value matches expected
    :param op_return_value:
    :param signed_hextx:
    :return:
    """
    logging.info('verifying op_return value for transaction')
    op_return_hash = signed_hextx[-72:-8]
    result = (op_return_value == op_return_hash)
    if not result:
        error_message = 'There was a problem verifying the transaction'
        raise UnverifiedDocumentError(error_message)
    logging.info('verified OP_RETURN')
