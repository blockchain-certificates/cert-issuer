import logging
import random
import time
from datetime import datetime

from issuer.errors import InsufficientFundsError
from issuer.models import TransactionCosts


COIN = 100000000   # satoshis in 1 btc
BYTES_PER_INPUT = 180
BYTES_PER_OUTPUT = 34
FIXED_EXTRA_BYTES = 10


def get_cost_for_certificate_batch(dust_threshold, recommended_fee_per_transaction, satoshi_per_byte, num_certificates,
                                   allow_transfer):
    """Per certificate, we pay 2*min_per_transaction (which is based on dust) + recommended fee. Note assumes 1 input
    per tx. We may also need to pay additional fees for splitting into temp addresses
    """
    fee_per_transaction = recommended_fee_per_transaction * COIN
    min_per_transaction = dust_threshold * COIN

    # plus additional fees for splitting
    if allow_transfer:
        split_transfer_fee = calculate_txfee(satoshi_per_byte, fee_per_transaction, 1, num_certificates)
    else:
        split_transfer_fee = 0

    return TransactionCosts(min_per_transaction, fee_per_transaction, num_certificates, split_transfer_fee)


def calculate_txfee(satoshi_per_byte, fee_per_transaction, num_inputs, num_outputs):
    """The course grained (hard-coded value) of something like 0.0001 BTC works great for standard transactions
    (one input, one output). However, it will cause a huge lag in more complex transactions (such as the one where the
    script spends a little bit of money to 10 temporary addresses). So the calculate_txfree is used to calculate the
    fee for these more complex transactions. We take the max of the default_tx_fee and the refined cost to ensure
    prompt processing

    See explanation of constants above

    """
    tx_size = (num_inputs * BYTES_PER_INPUT) + (num_outputs * BYTES_PER_OUTPUT) + FIXED_EXTRA_BYTES + num_inputs
    tx_fee = satoshi_per_byte * tx_size
    return max(tx_fee, fee_per_transaction)


class Wallet:
    def __init__(self, connector):
        self.connector = connector

    def login(self):
        return self.connector.login()

    def __get_balance(self, address, confirmations):
        return self.connector.get_balance(address, confirmations)

    def get_confirmed_balance(self, address):
        return self.__get_balance(address, 1)

    def get_unconfirmed_balance(self, address):
        return self.__get_balance(address, 0)

    def get_unspent_outputs(self, address):
        unspent_outputs = self.connector.get_unspent_outputs(address)

        if not unspent_outputs:
            logging.error('No money to spend at address %s', address)
            raise InsufficientFundsError('No money to spend at address {0}'.format(address))

        unspent_sorted = sorted(unspent_outputs, key=lambda x: hash(x.amount))
        return unspent_sorted

    def is_confirmed(self, address):
        """Checks if all the BTC in the address has been confirmed. Returns true if is has been confirmed and false if
         it has not."""

        confirmed_balance = self.get_confirmed_balance(address)
        unconfirmed_balance = self.get_unconfirmed_balance(address)

        if unconfirmed_balance and confirmed_balance:
            if int(confirmed_balance) == int(unconfirmed_balance):
                return True
        return False

    def pay_and_archive(self, from_address, issuing_address, cost, fee):
        self.connector.pay(from_address, issuing_address, cost, fee)
        self.archive(from_address)

    def send_to_addresses(self, storage_address, temp_addresses):
        return self.connector.send_to_addresses(storage_address, temp_addresses)

    def wait_for_confirmation(self, address):
        logging.info('Waiting for a pending transaction to be confirmed for address %s', address)
        benchmark = datetime.now()
        while True:
            confirmed_tx = self.is_confirmed(address)
            elapsed_time = str(datetime.now() - benchmark)
            if confirmed_tx:
                logging.info('It took %s to process the transaction', elapsed_time)
                break
            logging.info('Time: %s, waiting 30 seconds and then checking if transaction is confirmed', elapsed_time)
            time.sleep(30)
        return confirmed_tx

    def transfer_balance(self, storage_address, issuing_address, transaction_costs):
        """
        transfer balance to ensure enough is available for certificates
        The temporary addresses are used to subdivide the payments in order to break them up into individual spends.
        This way, we do not have to wait for one large input to be spent on the blockchain and confirmed (i.e. a little bit
        of the money spent and the rest return to the address). This allows us to issue 10 certificates in the time it
        would take to issue two normally.
        """

        # first make sure that there are no pending transactions for the storage address
        self.wait_for_confirmation(storage_address)

        logging.info('Creating %d temporary addresses...', transaction_costs.number_of_transactions)

        # TODO: I think we should only do this if there are >2 or 3 certs?
        temp_addresses = []
        for i in range(transaction_costs.number_of_transactions):
            temp_address_in = 'temp-address-%s' % i
            temp_address = self.connector.create_temp_address(temp_address_in)
            temp_addresses.append(temp_address)

        logging.info('Transferring BTC to temporary addresses...')

        self.connector.send_to_addresses(storage_address, temp_addresses, transaction_costs.transfer_split_fee)
        logging.info('Waiting for confirmation of transfer...')

        random_address = random.choice(temp_addresses)

        confirmed_tx = self.wait_for_confirmation(random_address)

        logging.info('Making transfer to issuing address...')
        for address in temp_addresses:
            self.pay_and_archive(address, issuing_address, transaction_costs.cost_per_transaction,
                                   transaction_costs.fee_per_transaction)
        self.wait_for_confirmation(issuing_address)
        logging.info('Transferred BTC needed for issuing certificates from issuing address...')

    def check_balance(self, issuing_address, transaction_costs):
        address_balance = self.get_confirmed_balance(issuing_address)
        amount_needed = transaction_costs.difference(address_balance)

        if amount_needed > 0:
            logging.error('Please add %s BTC to the address %s', amount_needed, issuing_address)
            raise InsufficientFundsError('Please add {} BTC to the address {}'.format(amount_needed, issuing_address))

