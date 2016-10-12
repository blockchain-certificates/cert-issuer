"""
Helpers for certificates
"""

import json
import logging

from bitcoin.signmessage import BitcoinMessage
from bitcoin.signmessage import VerifyMessage

from cert_issuer.errors import UnverifiedDocumentError, UnverifiedSignatureError


def verify_signature(uid, signed_certificate_file_name, issuing_address):
    # Throws an error if invalid
    logging.info('verifying signature for certificate with uid=%s:', uid)
    with open(signed_certificate_file_name) as in_file:
        do_verify_signature(issuing_address, in_file.read())
        logging.info('verified signature')


def do_verify_signature(address, signed_cert):
    signed_cert_json = json.loads(signed_cert)
    to_verify = signed_cert_json['assertion']['uid']
    message = BitcoinMessage(to_verify)
    signature = signed_cert_json['signature']
    verified = VerifyMessage(address, message, signature)
    if not verified:
        error_message = 'There was a problem with the signature for certificate uid={}'.format(
            signed_cert_json['assertion']['uid'])
        raise UnverifiedSignatureError(error_message)


def verify_transaction(op_return_value, signed_hextx):
    # Throws an error if invalid
    logging.info('verifying op_return value for transaction')
    op_return_hash = signed_hextx[-72:-8]
    result = (op_return_value == op_return_hash)
    if not result:
        error_message = 'There was a problem verifying the transaction'
        raise UnverifiedDocumentError(error_message)
    logging.info('verified OP_RETURN')
