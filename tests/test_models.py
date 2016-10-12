import unittest

from cert_issuer.models import TotalCosts, TransactionCosts


class TestModels(unittest.TestCase):

    def test_TotalCosts_no_split(self):
        issuing_cost = TransactionCosts(10, 4000, 60000)
        costs = TotalCosts(issuing_transaction_cost=issuing_cost, transfer_cost=None)
        self.assertEqual(60000, costs.total)

    def test_TransactionCosts_with_split(self):
        issuing_cost = TransactionCosts(10, 4000, 60000)
        transfer_cost = TransactionCosts(10, 4000, 50000)
        costs = TotalCosts(issuing_cost, transfer_cost)

        self.assertEqual(110000, costs.total)


if __name__ == '__main__':
    unittest.main()