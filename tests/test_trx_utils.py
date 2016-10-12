import unittest

from cert_issuer import trx_utils

from bitcoin.core import *
from bitcoin.core.script import OP_RETURN
from bitcoin.wallet import CBitcoinAddress

from pycoin.encoding import wif_to_secret_exponent
from pycoin.tx import *
from pycoin.tx.pay_to import build_hash160_lookup

from cert_issuer import helpers
from cert_issuer.helpers import internet_off_for_scope
from cert_issuer.models import TransactionCosts
import bitcoin.rpc
import requests
from bitcoin.core import COutPoint, CScript, CTransaction
from bitcoin.wallet import CBitcoinAddress

from cert_issuer.errors import UnrecognizedConnectorError, ConnectorError
from cert_issuer.helpers import unhexlify, hexlify
from pycoin.tx import Spendable
from pycoin.serialize import b2h, h2b
import io



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

    def test_create_trx(self):
        cost = TransactionCosts(0.0001, 0.0000275, 3)
        tx_input = Spendable(200, '18eKkAWyU9kvRNHPKxnZb6wwtPMrNmRRRA', h2b('8443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b154'), 0)
        tx_outs = [trx_utils.create_transaction_output('mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', 0.0000275)]
        tx = trx_utils.create_trx('TEST'.encode('utf-8'), cost, 'mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', tx_outs, tx_input)

        hextx = hexlify(tx.serialize())
        self.assertEquals(hextx, '01000000018443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b1540000000000ffffffff0300000000000000001976a914072a22e5913cd939904c46bbd0bc56755543384b88acc5000000000000001976a914072a22e5913cd939904c46bbd0bc56755543384b88ac0000000000000000066a045445535400000000')



if __name__ == '__main__':
    unittest.main()