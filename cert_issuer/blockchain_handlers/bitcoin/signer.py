import json
import logging

from bitcoin.signmessage import BitcoinMessage, SignMessage
from bitcoin.signmessage import VerifyMessage
from bitcoin.wallet import CBitcoinSecret
from pycoin.networks.registry import network_for_netcode
from pycoin.solve.utils import build_hash160_lookup

from cert_issuer.errors import UnverifiedSignatureError, UnableToSignTxError
from cert_issuer.helpers import to_pycoin_chain
from cert_issuer.models import Signer


class BitcoinSigner(Signer):
    def __init__(self, bitcoin_chain):
        self.bitcoin_chain = bitcoin_chain

    def sign_message(self, wif, message_to_sign):
        secret_key = CBitcoinSecret(wif)
        message = BitcoinMessage(message_to_sign)
        signature = SignMessage(secret_key, message)
        return str(signature, 'utf-8')

    def sign_transaction(self, wif, transaction_to_sign):
        netcode = to_pycoin_chain(self.bitcoin_chain)
        network = network_for_netcode(netcode)
        key = network.parse.wif(wif)
        secret_exponent = key.secret_exponent()
        lookup = build_hash160_lookup([secret_exponent])
        signed_transaction = transaction_to_sign.sign(lookup)
        # Because signing failures silently continue, first check that the inputs are signed
        for input in signed_transaction.txs_in:
            if len(input.script) == 0:
                logging.error('Unable to sign transaction. hextx=%s', signed_transaction.as_hex())
                raise UnableToSignTxError('Unable to sign transaction')
        return signed_transaction


def verify_message(address, message, signature):
    """
    Verify message was signed by the address
    :param address: signing address
    :param message: message to check
    :param signature: signature being tested
    :return:
    """
    bitcoin_message = BitcoinMessage(message)
    verified = VerifyMessage(address, bitcoin_message, signature)
    return verified


def verify_signature(uid, signed_cert_file_name, issuing_address):
    """
    Verify the certificate signature matches the expected. Double-check the uid field in the certificate and use
    VerifyMessage to confirm that the signature in the certificate matches the issuing_address.

    Raises error is verification fails.

    Raises UnverifiedSignatureError if signature is invalid

    :param uid:
    :param signed_cert_file_name:
    :param issuing_address:
    :return:
    """

    logging.info('verifying signature for certificate with uid=%s:', uid)
    with open(signed_cert_file_name) as in_file:
        signed_cert = in_file.read()
        signed_cert_json = json.loads(signed_cert)
        to_verify = uid
        signature = signed_cert_json['signature']
        verified = verify_message(issuing_address, to_verify, signature)
        if not verified:
            error_message = 'There was a problem with the signature for certificate uid={}'.format(uid)
            raise UnverifiedSignatureError(error_message)

        logging.info('verified signature')
