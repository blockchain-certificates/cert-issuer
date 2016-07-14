"""
Helpers for certificates
"""

import json
import logging

import hashlib
from bitcoin.signmessage import BitcoinMessage
from bitcoin.signmessage import VerifyMessage
from cert_issuer.errors import UnverifiedDocumentError, UnverifiedSignatureError
from chainpoint.MerkleTree import MerkleTree, sha256


def hash_certs(certificates_metadata):
    logging.info('hashing certificates')
    for uid, certificate_metadata in certificates_metadata.items():
        with open(certificate_metadata.signed_certificate_file_name, 'rb') as in_file, \
                open(certificate_metadata.certificate_hash_file_name, 'wb') as out_file:
            cert = in_file.read()
            hashed_cert = _hash_cert(cert)
            out_file.write(hashed_cert)


def _hash_cert(signed_certificate):
    return hashlib.sha256(signed_certificate).digest()


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


def verify_transaction(op_return_value, signed_transaction_file_name):
    # Throws an error if invalid
    logging.info('verifying op_return value for transaction')

    with open(signed_transaction_file_name) as unsent_tx_file:
        op_return_hash = unsent_tx_file.read()[-72:-8]
        result = (op_return_value == op_return_hash)
        if not result:
            error_message = 'There was a problem verifying the transaction'
            raise UnverifiedDocumentError(error_message)
    logging.info('verified OP_RETURN')


def build_merkle_tree(certificates_to_issue):
    tree = MerkleTree()
    for uid, certificate in certificates_to_issue.items():
        with open(certificate.signed_certificate_file_name, 'r') as in_file:
            certificate = in_file.read()
            tree.add_content(certificate)
    graph_json = tree.graph_json()
    with open('tree.json', 'w') as out_file:
        out_file.write(json.dumps(graph_json))
    return tree


def build_receipts(certificates_to_issue, tree):
    root = tree.merkle_root()
    for uid, certificate in certificates_to_issue.items():
        with open(certificate.signed_certificate_file_name, 'r') as in_file:
            certificate = in_file.read()
            proof = tree.merkle_proof(sha256(certificate))

            receipt = {'target': sha256(certificate),
                       'root': root,
                       'proof': json.loads(proof.get_json())
                       }

            with open(certificate.proof_file_name, 'w') as out_file:
                out_file.write(json.dumps(receipt))
