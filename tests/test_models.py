import unittest

from certificate_issuer.models import TransactionCosts


class TestModels(unittest.TestCase):

    def test_TransactionCosts_no_split(self):
        costs = TransactionCosts(3, 1, 5)
        self.assertEqual(15, costs.total)

    def test_TransactionCosts_with_split(self):
        costs = TransactionCosts(3, 1, 5, 6)
        self.assertEqual(21, costs.total)