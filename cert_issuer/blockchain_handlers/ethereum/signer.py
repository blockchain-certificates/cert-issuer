import logging

import web3
from eth_utils import to_hex

from cert_issuer.errors import UnableToSignTxError
from cert_issuer.models import Signer


class EthereumSigner(Signer):
    def __init__(self, ethereum_chain):
        self.ethereum_chain = ethereum_chain
        # Netcode ensures replay protection (see EIP155)
        if ethereum_chain.external_display_value == 'ethereumMainnet':
            self.netcode = 1
        elif ethereum_chain.external_display_value == 'ethereumRopsten':
            self.netcode = 3
        elif ethereum_chain.external_display_value == 'ethereumGoerli':
            self.netcode = 5
        elif ethereum_chain.external_display_value == 'ethereumSepolia':
            self.netcode = 11155111
        else:
            self.netcode = None

    # wif = unencrypted private key as string in the first line of the supplied private key file
    def sign_message(self, wif, message_to_sign):
        pass

    def sign_transaction(self, wif, transaction_to_sign):
        if isinstance(transaction_to_sign, dict):
            try:
                transaction_to_sign['chainId'] = self.netcode
                raw_tx = web3.Account.sign_transaction(transaction_to_sign, wif)['rawTransaction']
                raw_tx_hex = to_hex(raw_tx)
                return raw_tx_hex
            except Exception as msg:
                logging.error('error occurred when ETH signing transaction: %s', msg)
                return {'error': True, 'message': msg}
        else:
            raise UnableToSignTxError('"sign_transaction()" expects a dict representing an unsigned transaction with fields such as "gas", "to", "data", etc. run "$ python cert_issuer -h" for more information on transaction configuration.')
