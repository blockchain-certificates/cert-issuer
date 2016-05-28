import unittest

from issuer.models import TransactionCosts


class TestModels(unittest.TestCase):

    def test_TransactionCosts_no_split(self):
        costs = TransactionCosts(min_per_output=3, fee_per_transaction=1, number_of_transactions=5, transfer_split_fee=0)
        self.assertEqual(35, costs.total)

    def test_TransactionCosts_with_split(self):
        costs = TransactionCosts(min_per_output=3, fee_per_transaction=1, number_of_transactions=5, transfer_split_fee=6)
        self.assertEqual(41, costs.total)