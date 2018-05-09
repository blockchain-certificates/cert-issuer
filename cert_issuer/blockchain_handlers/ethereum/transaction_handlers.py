import logging

from pycoin.serialize import b2h

from cert_issuer.errors import InsufficientFundsError
from cert_issuer.blockchain_handlers.ethereum import tx_utils
from cert_issuer.models import TransactionHandler
from cert_issuer.signer import FinalizableSigner


# as the transaction format in Ethereum is different, the abstracted TransactionCreator doesn't satisfy
class EthereumTransactionCreator(object):
    def estimate_cost_for_certificate_batch(self):
        pass

    def create_transaction(self, tx_cost_constants, issuing_address, nonce, to_address, blockchain_bytes):
        gasprice = tx_cost_constants.get_gas_price()
        gaslimit = tx_cost_constants.get_gas_limit()

        transaction = tx_utils.create_ethereum_trx(
            issuing_address,
            nonce,
            to_address,
            blockchain_bytes,
            gasprice,
            gaslimit)

        return transaction


class EthereumTransactionHandler(TransactionHandler):
    def __init__(self, connector, tx_cost_constants, secret_manager, issuing_address, prepared_inputs=None,
                 transaction_creator=EthereumTransactionCreator()):
        self.connector = connector
        self.tx_cost_constants = tx_cost_constants
        self.secret_manager = secret_manager
        self.issuing_address = issuing_address
        # input transactions are not needed for Ether
        self.prepared_inputs = prepared_inputs
        self.transaction_creator = transaction_creator

    def ensure_balance(self):
        # testing etherscan api wrapper
        self.balance = self.connector.get_balance(self.issuing_address)

        # for now transaction cost will be a constant: (25000 gas estimate times 20Gwei gasprice) from tx_utils
        # can later be calculated inside EthereumTransaction_creator
        transaction_cost = self.tx_cost_constants.get_recommended_max_cost()
        logging.info('Total cost will be %d wei', transaction_cost)

        if transaction_cost > self.balance:
            error_message = 'Please add {} wei to the address {}'.format(
                transaction_cost - self.balance, self.issuing_address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def issue_transaction(self, blockchain_bytes):
        eth_data_field = b2h(blockchain_bytes)
        prepared_tx = self.create_transaction(blockchain_bytes)
        signed_tx = self.sign_transaction(prepared_tx)
        self.verify_transaction(signed_tx, eth_data_field)
        txid = self.broadcast_transaction(signed_tx)
        return txid

    def create_transaction(self, blockchain_bytes):
        if self.balance:
            # it is assumed here that the address has sufficient funds, as the ensure_balance has just been checked
            nonce = self.connector.get_address_nonce(self.issuing_address)
            # Transactions in the first iteration will be send to burn address
            toaddress = '0xdeaddeaddeaddeaddeaddeaddeaddeaddeaddead'
            tx = self.transaction_creator.create_transaction(self.tx_cost_constants, self.issuing_address, nonce,
                                                             toaddress, blockchain_bytes)

            prepared_tx = tx
            return prepared_tx
        else:
            raise InsufficientFundsError('Not sufficient ether to spend at: %s', self.issuing_address)

    def sign_transaction(self, prepared_tx):
        # stubbed from BitcoinTransactionHandler
        with FinalizableSigner(self.secret_manager) as signer:
            signed_tx = signer.sign_transaction(prepared_tx)

        logging.info('signed Ethereum trx = %s', signed_tx)
        return signed_tx

    def broadcast_transaction(self, signed_tx):
        txid = self.connector.broadcast_tx(signed_tx)
        return txid

    def verify_transaction(self, signed_tx, eth_data_field):
        tx_utils.verify_eth_transaction(signed_tx, eth_data_field)
