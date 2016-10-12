"""
Wallet for Blockchain Certificate issuing
"""
import logging

from cert_issuer.connectors import pay, get_balance, get_unspent_outputs
from cert_issuer.errors import InsufficientFundsError


class Wallet:
    """
    Wallet handles payment aspects of issuing Blockchain Certificates. It uses configurable connectors for checking
    balance and payments.
    """

    def get_unspent_outputs(self, address):
        unspent_outputs = get_unspent_outputs(address)

        if not unspent_outputs:
            error_message = 'No money to spend at address {}'.format(address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

        unspent_sorted = sorted(unspent_outputs, key=lambda x: hash(x.value))
        return unspent_sorted

    def send_payment(self, from_address, issuing_address, cost, fee):
        pay(from_address, issuing_address, cost, fee)

    def check_balance(self, address, transaction_costs):
        """Returns amount needed in wallet to perform transaction(s). A positive return value indicates funds are missing"""
        amount_needed = self.check_balance_no_throw(address, transaction_costs=transaction_costs)

        if amount_needed > 0:
            error_message = 'Please add {} satoshis to the address {}'.format(
                amount_needed, address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def check_balance_no_throw(self, address, transaction_costs):
        """Returns amount needed in wallet to perform transaction(s). A positive return value indicates funds are missing"""
        address_balance = get_balance(address, 'TODONETCODE')
        amount_needed = transaction_costs.difference(address_balance)
        return amount_needed
