import logging
import random
from abc import abstractmethod

from cert_issuer import tx_utils
from cert_issuer.errors import InsufficientFundsError
from cert_issuer.helpers import hexlify
from cert_issuer.signer import FinalizableSigner

# Estimate fees assuming worst case 3 inputs
ESTIMATE_NUM_INPUTS = 3

# Estimate fees assuming 1 output for change.
# Note that tx_utils calculations add on cost due to OP_RETURN size, so it doesn't need to be added here.
V2_NUM_OUTPUTS = 1


class TransactionHandler(object):
    @abstractmethod
    def ensure_balance(self):
        pass

    @abstractmethod
    def issue_transaction(self, op_return_bytes):
        pass


class TransactionCreator(object):
    @abstractmethod
    def estimate_cost_for_certificate_batch(self, tx_cost_constants, num_inputs=ESTIMATE_NUM_INPUTS):
        pass

    @abstractmethod
    def create_transaction(self, tx_cost_constants, issuing_address, inputs, op_return_value):
        pass


class TransactionV2Creator(TransactionCreator):
    def estimate_cost_for_certificate_batch(self, tx_cost_constants, num_inputs=ESTIMATE_NUM_INPUTS):
        total = tx_utils.calculate_tx_fee(tx_cost_constants, num_inputs, V2_NUM_OUTPUTS)
        return total

    def create_transaction(self, tx_cost_constants, issuing_address, inputs, op_return_value):
        fee = tx_utils.calculate_tx_fee(tx_cost_constants, len(inputs), V2_NUM_OUTPUTS)
        transaction = tx_utils.create_trx(
            op_return_value,
            fee,
            issuing_address,
            [],
            inputs)

        return transaction


class BitcoinTransactionHandler(TransactionHandler):
    def __init__(self, connector, tx_cost_constants, secret_manager, issuing_address, prepared_inputs=None,
                 transaction_creator=TransactionV2Creator()):
        self.connector = connector
        self.tx_cost_constants = tx_cost_constants
        self.secret_manager = secret_manager
        self.issuing_address = issuing_address
        self.prepared_inputs = prepared_inputs
        self.transaction_creator = transaction_creator

    def ensure_balance(self):
        # ensure the issuing address has sufficient balance
        balance = self.connector.get_balance(self.issuing_address)

        transaction_cost = self.transaction_creator.estimate_cost_for_certificate_batch(self.tx_cost_constants)
        logging.info('Total cost will be %d satoshis', transaction_cost)

        if transaction_cost > balance:
            error_message = 'Please add {} satoshis to the address {}'.format(
                transaction_cost - balance, self.issuing_address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def issue_transaction(self, op_return_bytes):
        op_return_value = hexlify(op_return_bytes)
        prepared_tx = self.create_transaction(op_return_bytes)
        signed_tx = self.sign_transaction(prepared_tx)
        self.verify_transaction(signed_tx, op_return_value)
        txid = self.broadcast_transaction(signed_tx)

        logging.info('Broadcast transaction with txid %s', txid)
        return txid

    def create_transaction(self, op_return_bytes):
        if self.prepared_inputs:
            inputs = self.prepared_inputs
        else:
            spendables = self.connector.get_unspent_outputs(self.issuing_address)
            if not spendables:
                error_message = 'No money to spend at address {}'.format(self.issuing_address)
                logging.error(error_message)
                raise InsufficientFundsError(error_message)

            cost = self.transaction_creator.estimate_cost_for_certificate_batch(self.tx_cost_constants)
            current_total = 0
            inputs = []
            random.shuffle(spendables)
            for s in spendables:
                inputs.append(s)
                current_total += s.coin_value
                if current_total > cost:
                    break

        tx = self.transaction_creator.create_transaction(self.tx_cost_constants, self.issuing_address, inputs,
                                                         op_return_bytes)
        hex_tx = hexlify(tx.serialize())
        logging.info('Unsigned hextx=%s', hex_tx)
        prepared_tx = tx_utils.prepare_tx_for_signing(hex_tx, inputs)
        return prepared_tx

    def sign_transaction(self, prepared_tx):
        with FinalizableSigner(self.secret_manager) as signer:
            signed_tx = signer.sign_transaction(prepared_tx)

        # log the actual byte count
        tx_byte_count = tx_utils.get_byte_count(signed_tx)
        logging.info('The actual transaction size is %d bytes', tx_byte_count)

        signed_hextx = signed_tx.as_hex()
        logging.info('Signed hextx=%s', signed_hextx)
        return signed_tx

    def verify_transaction(self, signed_tx, op_return_value):
        signed_hextx = signed_tx.as_hex()
        logging.info('Signed hextx=%s', signed_hextx)
        tx_utils.verify_transaction(signed_hextx, op_return_value)

    def broadcast_transaction(self, signed_tx):
        tx_id = self.connector.broadcast_tx(signed_tx)
        return tx_id
