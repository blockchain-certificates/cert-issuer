import unittest

from cert_issuer import trx_utils


SATOSHI_PER_BYTE=41


class TestTrxUtils(unittest.TestCase):

    def test_calculate_raw_tx_fee(self):
        result = trx_utils.calculate_txfee(satoshi_per_byte=SATOSHI_PER_BYTE, num_inputs=40, num_outputs=16,
                                           default_fee=10000)
        self.assertEqual(result, 267074)

    def test_calculate_raw_tx_size(self):
        result = trx_utils.calculate_raw_tx_size(num_inputs=40, num_outputs=16)
        self.assertEqual(result, 6514)

    def test_get_cost(self):
        result = trx_utils.get_cost(0.0001, 0.0000275, 41, 4)
        self.assertEqual(result.total, 23095)

        result = trx_utils.get_cost(0.0001, 0.0000275, 41, 1)
        self.assertEqual(result.total, 12750)