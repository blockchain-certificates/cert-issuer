import json
import logging
import os
import time

import requests
from bitcoin.signmessage import BitcoinMessage, SignMessage
from bitcoin.signmessage import VerifyMessage
from bitcoin.wallet import CBitcoinSecret
from pycoin.encoding import wif_to_secret_exponent
from pycoin.networks import wif_prefix_for_netcode
from pycoin.tx import TxOut, Tx
from pycoin.tx.pay_to import build_hash160_lookup

from cert_issuer.errors import UnverifiedSignatureError


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


class SecretManager(object):
    """
    Abstraction for a secret store. TODO: come up with better names.
    """

    def __init__(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def get_wif(self):
        pass


class FileSecretManager(SecretManager):
    def __init__(self, path_to_secret, disable_safe_mode):
        super().__init__()
        self.path_to_secret = path_to_secret
        self.disable_safe_mode = disable_safe_mode

    def start(self):
        if self.disable_safe_mode:
            check_internet_off(self.path_to_secret)
        else:
            logging.warning(
                'app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
                ' ensure this is what you want, since this is less secure')

    def stop(self):
        if self.disable_safe_mode:
            check_internet_on(self.path_to_secret)
        else:
            logging.warning(
                'app is configured to skip the wifi check when the USB is plugged in. Read the documentation to'
                ' ensure this is what you want, since this is less secure')

    def get_wif(self):
        return import_key(self.path_to_secret)


class Signer(object):
    def __init__(self, secret_manager):
        self.secret_manager = secret_manager

    def sign_tx(self, hex_tx, tx_input, netcode):
        """
        Sign the transaction with private key
        :param hex_tx:
        :param tx_input:
        :param netcode:
        :return:
        """
        logging.info('Signing tx with private key')

        self.secret_manager.start()
        wif = self.secret_manager.get_wif()

        transaction = Tx.from_hex(hex_tx)
        allowable_wif_prefixes = wif_prefix_for_netcode(netcode)

        se = wif_to_secret_exponent(wif, allowable_wif_prefixes)
        lookup = build_hash160_lookup([se])
        transaction.set_unspents([TxOut(coin_value=tx_input.coin_value, script=tx_input.script)])
        signed_tx = transaction.sign(lookup)
        self.secret_manager.stop()
        logging.info('Finished signing transaction')
        return signed_tx

    def sign_certs(self, certificates):
        """
        Sign certificates. Internet should be off for the scope of this function.
        :param certificates:
        :return:
        """
        logging.info('signing certificates')

        self.secret_manager.start()
        wif = self.secret_manager.get_wif()

        secret_key = CBitcoinSecret(wif)
        for _, certificate in certificates.items():
            with open(certificate.unsigned_cert_file_name, 'r') as cert_in, \
                    open(certificate.signed_cert_file_name, 'wb') as signed_cert:
                cert = _sign(cert_in.read(), secret_key)
                signed_cert.write(bytes(cert, 'utf-8'))
        self.secret_manager.stop()


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

        to_verify = signed_cert_json['assertion']['uid']
        signature = signed_cert_json['signature']
        message = BitcoinMessage(to_verify)
        verified = VerifyMessage(issuing_address, message, signature)
        if not verified:
            error_message = 'There was a problem with the signature for certificate uid={}'.format(
                signed_cert_json['assertion']['uid'])
            raise UnverifiedSignatureError(error_message)

        logging.info('verified signature')
