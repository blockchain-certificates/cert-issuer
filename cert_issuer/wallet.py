import logging
import time
from datetime import datetime

import random
from cert_issuer.errors import InsufficientFundsError


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
            error_message = 'No money to spend at address {}'.format(address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

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
        self.connector.archive(from_address)

    def send_to_addresses(self, storage_address, temp_addresses):
        return self.connector.send_to_addresses(
            storage_address, temp_addresses)

    def wait_for_confirmation(self, address):
        logging.info(
            'Determining if there are pending transactions to be confirmed for address %s', address)
        benchmark = datetime.now()
        confirmed_tx = False
        while True:
            confirmed_tx = self.is_confirmed(address)
            elapsed_time = str(datetime.now() - benchmark)
            if confirmed_tx:
                logging.info(
                    'It took %s to process the transaction', elapsed_time)
                break
            logging.info(
                'Time: %s, waiting 30 seconds and then checking if transaction is confirmed', elapsed_time)
            time.sleep(30)
        return confirmed_tx

    def check_balance(self, address, transaction_costs):
        """Check there is enough balance in the wallet. Throws error if funds are lacking"""
        amount_needed = self.calculate_funds_needed(address, transaction_costs)

        if amount_needed > 0:
            error_message = 'Please add {} satoshis to the address {}'.format(
                amount_needed, address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def calculate_funds_needed(self, address, transaction_costs):
        """Returns amount needed in wallet to perform transaction(s). A positive return value indicates funds are missing"""
        address_balance = self.get_confirmed_balance(address)
        amount_needed = transaction_costs.difference(address_balance)

        if amount_needed > 0:
            error_message = 'Please add {} satoshis to the address {}'.format(
                amount_needed, address)
            logging.warning(error_message)
        return amount_needed

    def transfer_balance(self, storage_address,
                         issuing_address, total_costs):
        """Transfer balance to ensure enough is available for certificates. The temporary addresses are used to subdivide
        the payments in order to break them up into individual spends. This way, we do not have to wait for one large
        input to be spent on the blockchain and confirmed (i.e. a little bit of the money spent and the rest return to
        the address). This is useful if issuing a larger number of certificates.
        """

        # first make sure that there are no pending transactions for the
        # storage address
        self.wait_for_confirmation(storage_address)

        logging.info('Creating %d temporary addresses...',
                     total_costs.number_of_transactions)

        temp_addresses = {}
        for i in range(total_costs.number_of_transactions):
            temp_address_in = 'temp-address-%s' % i
            temp_address = self.connector.create_temp_address(temp_address_in)
            # we need to add enough to cover the fee of the subsequent spend
            # from the temp address
            temp_addresses[temp_address] = total_costs.issuing_transaction_cost.total

        logging.info('Transferring BTC to temporary addresses...')

        self.connector.send_to_addresses(
            storage_address, temp_addresses, total_costs.transfer_split_fee)
        logging.info('Waiting for confirmation of transfer...')

        random_address = random.choice(list(temp_addresses.keys()))

        self.wait_for_confirmation(random_address)

        logging.info('Making transfer to issuing address...')
        for address in temp_addresses.keys():
            self.pay_and_archive(address, issuing_address, total_costs.issuing_transaction_cost.min_per_output,
                                 total_costs.issuing_transaction_cost.fee)
        self.wait_for_confirmation(issuing_address)
        logging.info(
            'Transferred BTC needed for issuing certificates from issuing address...')
