"""
Wallet for Blockchain Certificate issuing
"""
import logging

from cert_issuer.connectors import pay, get_balance
from cert_issuer.errors import InsufficientFundsError


class Wallet:
    """
    Wallet handles payment aspects of issuing Blockchain Certificates. It uses configurable connectors for checking
    balance and payments.
    """

    def send_payment(self, from_address, issuing_address, cost, fee):
        pay(from_address, issuing_address, cost, fee)

    def check_balance(self, address, transaction_costs):
        """
        Returns amount needed in wallet to perform transaction(s). A positive return value indicates funds are missing

        :param address:
        :param transaction_costs:
        :return:
        """

        amount_needed = self.check_balance_no_throw(address, transaction_costs=transaction_costs)

        if amount_needed > 0:
            error_message = 'Please add {} satoshis to the address {}'.format(
                amount_needed, address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def check_balance_no_throw(self, address, transaction_costs):
        """
        Returns amount needed in wallet to perform transaction(s). A positive return value indicates funds are missing
        :param address:
        :param transaction_costs:
        :return:
        """
        address_balance = get_balance(address)
        amount_needed = transaction_costs.difference(address_balance)
        return amount_needed
