import unittest

from cert_issuer.models import TransactionCosts


class TestModels(unittest.TestCase):

    def test_TransactionCosts_no_split(self):
        issuing_cost = TransactionCosts(10, 4000, 60000)
        self.assertEqual(60000, issuing_cost.total)

    def test_TransactionCosts_with_split(self):
        issuing_cost = TransactionCosts(10, 4000, 60000)
        issuing_cost.set_transfer_fee(10000)

        self.assertEqual(70000, issuing_cost.total)


if __name__ == '__main__':
    unittest.main()