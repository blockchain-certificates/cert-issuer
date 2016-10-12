import unittest

from pycoin.convention.tx_fee import recommended_fee_for_tx
from pycoin.serialize import h2b
from pycoin.tx import Spendable
from pycoin.tx import Tx

from cert_issuer import trx_utils
from cert_issuer.helpers import hexlify
from cert_issuer.models import TransactionCosts


MAINNET_TX = '0100000001ce379123234bc9662f3f00f2a9c59d5420fc9f9d5e1fd8881b8666e8c9def133000000006a473044022032d2d9c2a67d90eb5ea32d9a5e935b46080d4c62a1d53265555c78775e8f6f2102205c3469593995b9b76f8d24aa4285a50b72ca71661ca021cd219883f1a8f14abe012103704cf7aa5e4152639617d0b3f8bcd302e231bbda13b468cba1b12aa7be14f3b3ffffffff07be0a0000000000001976a91464799d48941b0fbfdb4a7ee6340840fb2eb5c2c388acbe0a0000000000001976a914c615ecb52f6e877df0621f4b36bdb25410ec22c388acbe0a0000000000001976a9144e9862ff1c4041b7d083fe30cf5f68f7bedb321b88acbe0a0000000000001976a914413df7bf4a41f2e8a1366fcf7352885e6c88964b88acbe0a0000000000001976a914fabc1ff527531581b4a4c58f13bd088e274122bc88acbb810000000000001976a914fcbe34aa288a91eab1f0fe93353997ec6aa3594088ac0000000000000000226a2068f3ede17fdb67ffd4a5164b5687a71f9fbb68da803b803935720f2aa38f772800000000'


class TestTrxUtils(unittest.TestCase):

    def test_verify_transaction(self):
        cost = TransactionCosts(0.0001, 0.0000275, 3)
        tx_input = Spendable(200, '18eKkAWyU9kvRNHPKxnZb6wwtPMrNmRRRA', h2b('8443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b154'), 0)
        tx_outs = [trx_utils.create_transaction_output('mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', 0.0000275)]
        op_return_val = h2b('e9cee71ab932fde863338d08be4de9dfe39ea049bdafb342ce659ec5450b69ae')
        tx = trx_utils.create_trx(op_return_val, cost, 'mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', tx_outs, tx_input)

        hextx = hexlify(tx.serialize())

        trx_utils.verify_transaction(hextx, hexlify(op_return_val))

    def test_calculate_raw_tx_fee(self):
        result = trx_utils.calculate_txfee(num_inputs=40, num_outputs=16)
        self.assertEqual(result, 267074)

    def test_calculate_raw_tx_size(self):
        result = trx_utils.calculate_raw_tx_size(num_inputs=40, num_outputs=16)

        self.assertEqual(result, 6514)

    def test_get_cost(self):
        result = trx_utils.get_cost(4)
        self.assertEqual(result.total, 23095)

        result = trx_utils.get_cost(1)
        self.assertEqual(result.total, 12750)

    def test_create_trx(self):
        cost = TransactionCosts(0.0001, 0.0000275, 3)
        tx_input = Spendable(200, '18eKkAWyU9kvRNHPKxnZb6wwtPMrNmRRRA', h2b('8443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b154'), 0)
        tx_outs = [trx_utils.create_transaction_output('mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', 0.0000275)]
        tx = trx_utils.create_trx('TEST'.encode('utf-8'), cost, 'mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', tx_outs, tx_input)
        hextx = hexlify(tx.serialize())
        self.assertEquals(hextx, '01000000018443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b1540000000000ffffffff0300000000000000001976a914072a22e5913cd939904c46bbd0bc56755543384b88acc5000000000000001976a914072a22e5913cd939904c46bbd0bc56755543384b88ac0000000000000000066a045445535400000000')


    def test_compare_cost(self):
        cost = trx_utils.get_cost( 1)
        tx_input = Spendable(200, '18eKkAWyU9kvRNHPKxnZb6wwtPMrNmRRRA',
                             h2b('8443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b154'), 0)
        tx_outs = [trx_utils.create_transaction_output('mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', 0.0000275)]
        tx = trx_utils.create_trx('TEST'.encode('utf-8'), cost, 'mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', tx_outs, tx_input)

        tx2 = Tx.from_hex(MAINNET_TX)
        rec = recommended_fee_for_tx(tx2)

        print(rec)

        import io
        s = io.BytesIO()
        tx2.stream(s)
        tx_byte_count = len(s.getvalue())
        them = ((999 + tx_byte_count) // 1000)
        my_byte_count = trx_utils.calculate_raw_tx_size(num_inputs=1, num_outputs=6)
        print(tx_byte_count)



if __name__ == '__main__':
    unittest.main()