import rlp
from ethereum import transactions
from ethereum.utils import encode_hex

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
        else:
            self.netcode = None

    # wif = unencrypted private key as string in the first line of the supplied private key file
    def sign_message(self, wif, message_to_sign):
        pass

    def sign_transaction(self, wif, transaction_to_sign):
        ##try to sign the transaction.

        if isinstance(transaction_to_sign, transactions.Transaction):
            try:
                raw_tx = rlp.encode(transaction_to_sign.sign(wif, self.netcode))
                raw_tx_hex = encode_hex(raw_tx)
                return raw_tx_hex
            except Exception as msg:
                return {'error': True, 'message': msg}
        else:
            raise UnableToSignTxError('You are trying to sign a non transaction type')
