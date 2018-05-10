import io
import unittest

from bitcoin import SelectParams
from pycoin.serialize import b2h, h2b
from pycoin.tx.Spendable import Spendable
from pycoin.tx.Tx import Tx

from cert_issuer.blockchain_handlers.bitcoin import BitcoinTransactionCostConstants, tx_utils

MAINNET_TX = '0100000001ce379123234bc9662f3f00f2a9c59d5420fc9f9d5e1fd8881b8666e8c9def133000000006a473044022032d2d9c2a67d90eb5ea32d9a5e935b46080d4c62a1d53265555c78775e8f6f2102205c3469593995b9b76f8d24aa4285a50b72ca71661ca021cd219883f1a8f14abe012103704cf7aa5e4152639617d0b3f8bcd302e231bbda13b468cba1b12aa7be14f3b3ffffffff07be0a0000000000001976a91464799d48941b0fbfdb4a7ee6340840fb2eb5c2c388acbe0a0000000000001976a914c615ecb52f6e877df0621f4b36bdb25410ec22c388acbe0a0000000000001976a9144e9862ff1c4041b7d083fe30cf5f68f7bedb321b88acbe0a0000000000001976a914413df7bf4a41f2e8a1366fcf7352885e6c88964b88acbe0a0000000000001976a914fabc1ff527531581b4a4c58f13bd088e274122bc88acbb810000000000001976a914fcbe34aa288a91eab1f0fe93353997ec6aa3594088ac0000000000000000226a2068f3ede17fdb67ffd4a5164b5687a71f9fbb68da803b803935720f2aa38f772800000000'


class TestTrxUtils(unittest.TestCase):
    def test_verify_transaction(self):
        SelectParams('testnet')
        b = h2b('8443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b154')
        tx_input = Spendable(200, b'18eKkAWyU9kvRNHPKxnZb6wwtPMrNmRRRA', b, 0)
        tx_outs = [tx_utils.create_transaction_output('mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', 0.0000275)]
        op_return_val = h2b('e9cee71ab932fde863338d08be4de9dfe39ea049bdafb342ce659ec5450b69ae')
        tx = tx_utils.create_trx(op_return_val, 3, 'mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', tx_outs, [tx_input])

        hextx = b2h(tx.serialize())

        tx_utils.verify_transaction(hextx, b2h(op_return_val))

    def test_calculate_raw_tx_size(self):
        result = tx_utils.calculate_raw_tx_size(num_inputs=40, num_outputs=16)
        self.assertEqual(result, 6514)

    def test_calculate_raw_tx_size_with_op_return(self):
        estimated_byte_count = tx_utils.calculate_raw_tx_size_with_op_return(num_inputs=1, num_outputs=600)
        self.assertEquals(estimated_byte_count, 20602)

    def test_calculate_raw_tx_size_with_op_return_2(self):
        estimated_byte_count = tx_utils.calculate_raw_tx_size_with_op_return(num_inputs=1, num_outputs=2000)
        self.assertEquals(estimated_byte_count, 68202)

    def test_calculate_raw_tx_size_with_op_return_3(self):
        estimated_byte_count = tx_utils.calculate_raw_tx_size_with_op_return(num_inputs=1, num_outputs=4000)
        self.assertEquals(estimated_byte_count, 136202)

    def test_create_trx(self):
        SelectParams('testnet')
        b = h2b('8443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b154')
        tx_input = Spendable(200, b'18eKkAWyU9kvRNHPKxnZb6wwtPMrNmRRRA',
                             b, 0)
        tx_outs = [tx_utils.create_transaction_output('mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', 0.0000275)]
        tx = tx_utils.create_trx('TEST'.encode('utf-8'), 3, 'mgAqW5ZCnEp7fjvpj8RUL3WxsBy8rcDcCi', tx_outs, [tx_input])
        hextx = b2h(tx.serialize())
        self.assertEquals(hextx,
                          '01000000018443b07464c762d7fb404ea918a5ac9b3618d5cd6a0c5ea6e4dd5d7bbe28b1540000000000ffffffff0300000000000000001976a914072a22e5913cd939904c46bbd0bc56755543384b88acc5000000000000001976a914072a22e5913cd939904c46bbd0bc56755543384b88ac0000000000000000066a045445535400000000')

    def test_compare_cost(self):
        """
        Compare our size estimation with a known transaction. The transaction contains 1 input, 6 outputs, and 1
        OP_RETURN

        Note that the estimation may be off +/- the number of inputs, which is why the estimate was off by 1 in this
        case.
        :return:
        """

        tx = Tx.from_hex(
            '0100000001ae17c5db3174b46ae2bdc911c25df6bc3ce88092256b6f6e564989693ecf67fc030000006b483045022100b0cfd576dd30bbdf6fd11e0d6118c59b6c6f8e7bf6513d323c7f9f5f8296bef102200174a28e28c792425b71155df99ea6110cdb67d3567792f1696e61424c1f67400121037175dfbeecd8b5a54eb5ad9a696f15b7b39da2ea7d67b4cd7a3299bb95e28884ffffffff07be0a0000000000001976a91481c706f7e6b2d9546169c1e76f50a3ee18e1e1d788acbe0a0000000000001976a914c2b9a62457e35bef48ef350a00622b1e63394d4588acbe0a0000000000001976a91481c706f7e6b2d9546169c1e76f50a3ee18e1e1d788acbe0a0000000000001976a914c2b9a62457e35bef48ef350a00622b1e63394d4588acbe0a0000000000001976a914cc0a909c4c83068be8b45d69b60a6f09c2be0fda88ac5627cb1d000000001976a9144103222e7c72b869c5e47bfe86702684531f2c9088ac0000000000000000226a206f308c70afcfcb0311ad0de989b80904fb54d9131fd3ab2187b89ca9601adab000000000')
        s = io.BytesIO()
        tx.stream(s)
        tx_byte_count = len(s.getvalue())

        estimated_byte_count = tx_utils.calculate_raw_tx_size_with_op_return(num_inputs=1, num_outputs=6)
        self.assertEquals(estimated_byte_count, tx_byte_count + 1)

    def test_calculate_tx_fee_1(self):
        cost_constants = BitcoinTransactionCostConstants(0.0001, 0.0000275, 41)
        total = tx_utils.calculate_tx_total(cost_constants, 40, 16)
        self.assertEqual(total, 312837)

    def test_get_cost_1(self):
        cost_constants = BitcoinTransactionCostConstants(0.0001, 0.0000275, 41)
        total = tx_utils.calculate_tx_total(cost_constants, 1, 1)
        self.assertEqual(total, 12750)

    def test_get_cost_2(self):
        cost_constants = BitcoinTransactionCostConstants(0.0001, 0.0000275, 41)
        total = tx_utils.calculate_tx_total(cost_constants, 1, 4)
        self.assertEqual(total, 24858)

    def test_get_cost_3(self):
        cost_constants = BitcoinTransactionCostConstants(0.0001, 0.0000275, 41)
        total = tx_utils.calculate_tx_total(cost_constants, 1, 1000)
        self.assertEqual(total, 4152282)

    def test_get_cost_4(self):
        cost_constants = BitcoinTransactionCostConstants(0.0001, 0.0000275, 41)
        total = tx_utils.calculate_tx_total(cost_constants, 1, 2000)
        self.assertEqual(total, 8296282)


if __name__ == '__main__':
    unittest.main()
