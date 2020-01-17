import rlp
# from ethereum import transactions
# from ethereum.utils import encode_hex
from web3 import Web3, HTTPProvider

from cert_issuer.errors import UnableToSignTxError
from cert_issuer.models import Signer


class EthereumSCSigner(Signer):
    def __init__(self, ethereum_chain):
        self.ethereum_chain = ethereum_chain
        # Netcode ensures replay protection (see EIP155)
        if ethereum_chain.external_display_value == 'ethereumMainnet':
            self.netcode = 1
        elif ethereum_chain.external_display_value == 'ethereumRopsten':
            self.netcode = 3
        else:
            self.netcode = None

    # wif = unencrypted private key as string in the first line of the supplied private key file
    def sign_message(self, wif, message_to_sign):
        pass

    def sign_transaction(self, wif, transaction_to_sign):
        # try to sign the transaction.

        self.w3 = Web3(HTTPProvider())
        acct = self.w3.eth.account.from_key(wif)
        
        try:
            signed_tx = acct.sign_transaction(transaction_to_sign)
            return signed_tx
        except Exception as msg:
            raise UnableToSignTxError('You are trying to sign a non transaction type')
