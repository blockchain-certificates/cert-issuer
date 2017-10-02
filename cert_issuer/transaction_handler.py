import logging
import random
from abc import abstractmethod

from pycoin.serialize import b2h

from cert_issuer import tx_utils
from cert_issuer.errors import InsufficientFundsError
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
    def issue_transaction(self, blockchain_bytes):
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
##as the transaction format in Ethereum is different, the abstracted TransactionCreator doesn't satisfy
class EthereumTransactionCreator(object):
    def estimate_cost_for_certificate_batch(self):
        pass
    
    def create_transaction(self,tx_cost_constants, issuing_address, nonce, to_address, blockchain_bytes):
        #TODO: For a future iteration a better gasprice & gas limit calculation from the tx_cost_constants be done.
        #For now hardcoded constants are fine
        gasprice = tx_cost_constants.get_gas_price()
        gaslimit = tx_cost_constants.get_gas_limit()

        transaction = tx_utils.create_Ethereum_trx(
            issuing_address,
            nonce,
            to_address,
            blockchain_bytes,
            gasprice,
            gaslimit)

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

    def issue_transaction(self, blockchain_bytes):
        op_return_value = b2h(blockchain_bytes)
        prepared_tx = self.create_transaction(blockchain_bytes)
        signed_tx = self.sign_transaction(prepared_tx)
        self.verify_transaction(signed_tx, op_return_value)
        txid = self.broadcast_transaction(signed_tx)
        #this logging is already done in issuer
        #logging.info('Broadcast transaction with txid %s', txid)
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
        hex_tx = b2h(tx.serialize())
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

class EthereumTransactionHandler(TransactionHandler):
    def __init__(self, connector, tx_cost_constants, secret_manager, issuing_address, prepared_inputs=None,
                 transaction_creator=EthereumTransactionCreator()):
        self.connector=connector
        self.tx_cost_constants=tx_cost_constants
        self.secret_manager=secret_manager
        self.issuing_address=issuing_address
        #input transactions are not needed for Ether
        self.prepared_inputs=prepared_inputs
        self.transaction_creator=transaction_creator

    def ensure_balance(self):
        #testing etherscan api wrapper
        balance = self.connector.get_balance(self.issuing_address)

        #for now transaction cost will be a constant: (25000 gas estimate times 20Gwei gasprice) from tx_utils
        #can later be calculated inside EthereumTransaction_creator
        transaction_cost = self.tx_cost_constants.get_recommended_max_cost()
        logging.info('Total cost will be %d wei', transaction_cost)

        if transaction_cost > balance:
            error_message = 'Please add {} wei to the address {}'.format(
                transaction_cost - balance, self.issuing_address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def issue_transaction(self, blockchain_bytes):
        EtherDataField = b2h(blockchain_bytes)
        prepared_tx = self.create_transaction(blockchain_bytes)
        signed_tx = self.sign_transaction(prepared_tx)
        ##TODO: verify step
        txid = self.broadcast_transaction(signed_tx)
        
        ##'WIP'
        return txid

    def create_transaction(self, blockchain_bytes):
        ##it is assumed here that the address has sufficient funds, as the ensure_balance has just been checked
        nonce = self.connector.get_address_nonce(self.issuing_address)
        #Transactions in the first iteration will be send to burn address
        toaddress = '0xdeaddeaddeaddeaddeaddeaddeaddeaddeaddead'
        tx = self.transaction_creator.create_transaction(self.tx_cost_constants, self.issuing_address, nonce, toaddress, blockchain_bytes)
            
        ##TODO: transform transaction into prepared transaction format.
        prepared_tx = tx
        return prepared_tx

    def sign_transaction(self, prepared_tx):
        ##stubbed from BitcoinTransactionHandler
        with FinalizableSigner(self.secret_manager) as signer:
            signed_tx = signer.sign_transaction(prepared_tx)

        logging.info('signed Ethereum trx = %s', signed_tx)
        return signed_tx

    def broadcast_transaction(self, signed_tx):
        txid = self.connector.broadcast_tx(signed_tx)
        return txid

class MockTransactionHandler(TransactionHandler):
    def ensure_balance(self):
        pass

    def issue_transaction(self, op_return_bytes):
        return 'This has not been issued on a blockchain and is for testing only'
