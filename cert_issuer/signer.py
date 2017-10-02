import json
import logging
import os
import time
from abc import abstractmethod

import requests
from bitcoin.signmessage import BitcoinMessage, SignMessage
from bitcoin.signmessage import VerifyMessage
from bitcoin.wallet import CBitcoinSecret
from pycoin.encoding import wif_to_secret_exponent
from pycoin.networks import wif_prefix_for_netcode
from pycoin.tx.pay_to import build_hash160_lookup

from cert_issuer.errors import UnverifiedSignatureError, UnableToSignTxError

import rlp


def import_key(secrets_file_path):
    with open(secrets_file_path) as key_file:
        key = key_file.read().strip()
    return key


def internet_on():
    """Pings Google to see if the internet is on. If online, returns true. If offline, returns false."""
    try:
        requests.get('http://google.com')
        return True
    except requests.exceptions.RequestException:
        return False


def check_internet_off(secrets_file_path):
    """If internet off and USB plugged in, returns true. Else, continues to wait..."""
    while True:
        if internet_on() is False and os.path.exists(secrets_file_path):
            break
        else:
            print("Turn off your internet and plug in your USB to continue...")
            time.sleep(10)
    return True


def check_internet_on(secrets_file_path):
    """If internet on and USB unplugged, returns true. Else, continues to wait..."""
    while True:
        if internet_on() is True and not os.path.exists(secrets_file_path):
            break
        else:
            print("Turn on your internet and unplug your USB to continue...")
            time.sleep(10)
    return True


def initialize_signer(app_config):
    path_to_secret = os.path.join(app_config.usb_name, app_config.key_file)
    if app_config.blockchain == 'bitcoin':
        signer = BitcoinSigner(bitcoin_chain=app_config.bitcoin_chain_for_pycoin)
    elif app_config.blockchain == 'ethereum':
        signer = EthereumSigner(ethereum_chain=app_config.ethereum_chain)
    else:
        logging.error('Trying to sign to unknown blockchain')
    
    secret_manager = FileSecretManager(signer=signer, path_to_secret=path_to_secret,
                                       safe_mode=app_config.safe_mode, issuing_address=app_config.issuing_address)
    return secret_manager


class Signer(object):
    """
    Abstraction for a component that can sign.
    """

    def __init__(self):
        pass

    @abstractmethod
    def sign_message(self, wif, message_to_sign):
        pass

    @abstractmethod
    def sign_transaction(self, wif, transaction_to_sign):
        pass


class BitcoinSigner(Signer):
    def __init__(self, bitcoin_chain):
        self.bitcoin_chain = bitcoin_chain
        self.allowable_wif_prefixes = wif_prefix_for_netcode(bitcoin_chain.netcode)

    def sign_message(self, wif, message_to_sign):
        secret_key = CBitcoinSecret(wif)
        message = BitcoinMessage(message_to_sign)
        signature = SignMessage(secret_key, message)
        return str(signature, 'utf-8')

    def sign_transaction(self, wif, transaction_to_sign):
        secret_exponent = wif_to_secret_exponent(wif, self.allowable_wif_prefixes)
        lookup = build_hash160_lookup([secret_exponent])
        signed_transaction = transaction_to_sign.sign(lookup)
        # Because signing failures silently continue, first check that the inputs are signed
        for input in signed_transaction.txs_in:
            if len(input.script) == 0:
                logging.error('Unable to sign transaction. hextx=%s', signed_transaction.as_hex())
                raise UnableToSignTxError('Unable to sign transaction')
        return signed_transaction

class EthereumSigner(Signer):
    def __init__(self, ethereum_chain):
        self.ethereum_chain = ethereum_chain

    #wif = priv key in this example
    def sign_message(self, wif, message_to_sign):
        pass
    
    def sign_transaction(self, wif, transaction_to_sign):
        ##try to sign the transaction.
        try:
            return { 'error':False, 'sign':rlp.encode(transaction_to_sign.sign(wif)).encode('hex') }
        except Exception as msg:
            return { 'error':True, 'message':msg }
        


class SecretManager(object):
    def __init__(self, signer):
        self.signer = signer
        self.wif = None

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def sign_message(self, message_to_sign):
        return self.signer.sign_message(self.wif, message_to_sign)

    def sign_transaction(self, transaction_to_sign):
        return self.signer.sign_transaction(self.wif, transaction_to_sign)


class FileSecretManager(SecretManager):
    def __init__(self, signer, path_to_secret, safe_mode=True, issuing_address=None):
        super().__init__(signer)
        self.path_to_secret = path_to_secret
        self.safe_mode = safe_mode
        self.issuing_address = issuing_address

    def start(self):
        if self.safe_mode:
            check_internet_off(self.path_to_secret)
        else:
            logging.warning(
                'app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
                ' ensure this is what you want, since this is less secure')

        self.wif = import_key(self.path_to_secret)

    def stop(self):
        self.wif = None
        if self.safe_mode:
            check_internet_on(self.path_to_secret)
        else:
            logging.warning(
                'app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
                ' ensure this is what you want, since this is less secure')


class FinalizableSigner(object):
    def __init__(self, secret_manager):
        self.secret_manager = secret_manager

    def __enter__(self):
        logging.info('Starting finalizable signer')
        self.secret_manager.start()
        return self.secret_manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info('Stopping finalizable signer')
        self.secret_manager.stop()


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
