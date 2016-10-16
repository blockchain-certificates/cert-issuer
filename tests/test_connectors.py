import unittest

import bitcoin.rpc
from bitcoin.core import COutPoint, lx, x, CScript
from bitcoin.core.script import OP_EQUALVERIFY, OP_CHECKSIG, OP_DUP, OP_HASH160
from bitcoin.wallet import P2PKHBitcoinAddress
from mock import patch
from pycoin.tx import Tx

from cert_issuer.connectors import broadcast_tx, get_unspent_outputs, get_balance, BitcoindConnector
from cert_issuer.helpers import hexlify

TESTNET_TX = '010000000137e6a590428144e64cf008beb6e3193efee5a1a4ddfbbd48d10a12025b88c23c00000000fd5d0100473044022024959a1439e7e364c32f012a7e46dfa2d8cfa036ccdf230e9b3642fb9cdd4341022048292d0dbed226fadeae36b20627b50a3351456f164cae2923dba897995843c701483045022100e6dbcfb4ae35322e5c05688a6afcb144ab347654c217c9a3b2e963c2447418e702205cb639b549c7a9eace7d59ff2ce7c23167d60a214e6c9c011ce93317063850de014cc95241048aa0d470b7a9328889c84ef0291ed30346986e22558e80c3ae06199391eae21308a00cdcfb34febc0ea9c80dfd16b01f26c7ec67593cb8ab474aca8fa1d7029d4104cf54956634c4d0bdaf00e6b1871c089b7a892d0fecc077f03b91e8d4d146861b0a4fdd237891a9819c878984d4b123f6fe92d9bbc05873a1bb4fe510145bf369410471843c33b2971e4944c73d4500abd6f61f7edf9ec919c408cbe12a6c9132d2cb8ebed8253322760d5ec6081165e0ab68900683de503f1544f03816d47fec699a53aeffffffff09d29e91010000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f8727ed19190000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f874eda33320000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f879db467640000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f87a43d23030000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f87497b46060000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f87d29e91010000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f8793f68c0c0000000017a9145629021f7668d4ec310ac5e99701a6d6cf95eb8f8716400e00000000001976a9146efcf883b4b6f9997be9a0600f6c095fe2bd2d9288ac00000000'
MAINNET_TX = '0100000001ce379123234bc9662f3f00f2a9c59d5420fc9f9d5e1fd8881b8666e8c9def133000000006a473044022032d2d9c2a67d90eb5ea32d9a5e935b46080d4c62a1d53265555c78775e8f6f2102205c3469593995b9b76f8d24aa4285a50b72ca71661ca021cd219883f1a8f14abe012103704cf7aa5e4152639617d0b3f8bcd302e231bbda13b468cba1b12aa7be14f3b3ffffffff07be0a0000000000001976a91464799d48941b0fbfdb4a7ee6340840fb2eb5c2c388acbe0a0000000000001976a914c615ecb52f6e877df0621f4b36bdb25410ec22c388acbe0a0000000000001976a9144e9862ff1c4041b7d083fe30cf5f68f7bedb321b88acbe0a0000000000001976a914413df7bf4a41f2e8a1366fcf7352885e6c88964b88acbe0a0000000000001976a914fabc1ff527531581b4a4c58f13bd088e274122bc88acbb810000000000001976a914fcbe34aa288a91eab1f0fe93353997ec6aa3594088ac0000000000000000226a2068f3ede17fdb67ffd4a5164b5687a71f9fbb68da803b803935720f2aa38f772800000000'


def mock_listunspent_testnet(self, addrs):

    output1 = {'outpoint': COutPoint(lx('34eb81bc0d1a822369f75174fd4916b1ec490d8fbcba33168e820cc78a52f608'), 0),
               'confirmations': 62952, 'address': P2PKHBitcoinAddress('mz7poFND7hVGRtPWjiZizcCnjf6wEDWjjT'),
               'spendable': False, 'amount': 49000000, 'solvable': False, 'scriptPubKey': CScript(
            [OP_DUP, OP_HASH160, x('cc0a909c4c83068be8b45d69b60a6f09c2be0fda'), OP_EQUALVERIFY, OP_CHECKSIG]),
               'account': ''}
    output2 = {'address': P2PKHBitcoinAddress('mz7poFND7hVGRtPWjiZizcCnjf6wEDWjjT'), 'amount': 2750, 'account': '',
               'spendable': False, 'solvable': False, 'confirmations': 62932,
               'outpoint': COutPoint(lx('6773785b4dc5d2cced67d26fc0820329307a8e10dfaef50d506924984387bf0b'), 1),
               'scriptPubKey': CScript(
                   [OP_DUP, OP_HASH160, x('cc0a909c4c83068be8b45d69b60a6f09c2be0fda'), OP_EQUALVERIFY,
                    OP_CHECKSIG])}
    output3 = {'address': P2PKHBitcoinAddress('mz7poFND7hVGRtPWjiZizcCnjf6wEDWjjT'), 'amount': 2750, 'account': '',
               'spendable': False, 'solvable': False, 'confirmations': 62932,
               'outpoint': COutPoint(lx('6773785b4dc5d2cced67d26fc0820329307a8e10dfaef50d506924984387bf0b'), 5),
               'scriptPubKey': CScript(
                   [OP_DUP, OP_HASH160, x('cc0a909c4c83068be8b45d69b60a6f09c2be0fda'), OP_EQUALVERIFY,
                    OP_CHECKSIG])}
    unspent_outputs = [output1, output2, output3]
    return unspent_outputs

def mock_listunspent_mainnet(self, addrs):
    output1 = {'outpoint': COutPoint(lx('34eb81bc0d1a822369f75174fd4916b1ec490d8fbcba33168e820cc78a52f608'), 0),
               'confirmations': 123, 'address': P2PKHBitcoinAddress('13yNf3azc8sUrjf6UFjUCRZx4B6JnQ4XeJ'),
               'spendable': False, 'amount': 6342, 'solvable': False, 'scriptPubKey': CScript(
            [OP_DUP, OP_HASH160, x('cc0a909c4c83068be8b45d69b60a6f09c2be0fda'), OP_EQUALVERIFY, OP_CHECKSIG]),
               'account': ''}
    output2 = {'address': P2PKHBitcoinAddress('13yNf3azc8sUrjf6UFjUCRZx4B6JnQ4XeJ'), 'amount': 2750, 'account': '',
               'spendable': False, 'solvable': False, 'confirmations': 456,
               'outpoint': COutPoint(lx('6773785b4dc5d2cced67d26fc0820329307a8e10dfaef50d506924984387bf0b'), 1),
               'scriptPubKey': CScript(
                   [OP_DUP, OP_HASH160, x('cc0a909c4c83068be8b45d69b60a6f09c2be0fda'), OP_EQUALVERIFY,
                    OP_CHECKSIG])}
    unspent_outputs = [output1, output2]
    return unspent_outputs


def mock_init(self):
    pass

def mock_broadcast(transaction):
    return

class TestConnectors(unittest.TestCase):

    @patch.object(bitcoin.rpc.Proxy, 'listunspent', mock_listunspent_testnet)
    def test_bitcoind_connector_spendables(self):
        bc = BitcoindConnector('XTN')
        spendables = bc.spendables_for_address('mz7poFND7hVGRtPWjiZizcCnjf6wEDWjjT')
        self.assertEquals(len(spendables), 3)
        self.assertEquals(hexlify(spendables[0].tx_hash),
                          '08f6528ac70c828e1633babc8f0d49ecb11649fd7451f76923821a0dbc81eb34')
        self.assertEquals(spendables[0].coin_value, 49000000)
        self.assertEquals(spendables[1].coin_value, 2750)
        self.assertEquals(spendables[2].coin_value, 2750)

    @patch.object(bitcoin.rpc.Proxy, '__init__', mock_init)
    @patch.object(bitcoin.rpc.Proxy, 'sendrawtransaction', mock_broadcast)
    def test_broadcast_tx_mainnet(self):
        """
        Broadcasting tests fail because the transaction has already been pushed. So we're looking for a 'transaction
        already in blockchain' error
        """
        try:
            tx = Tx.from_hex(MAINNET_TX)
            broadcast_tx(tx)
            self.assertTrue(False)
        except Exception as e:
            self.assertTrue('already in block chain', str(e.args[0]))
            return
        self.assertTrue(False)

    @patch.object(bitcoin.rpc.Proxy, '__init__', mock_init)
    @patch.object(bitcoin.rpc.Proxy, 'listunspent', mock_listunspent_testnet)
    def test_bitcoind_connector_balance(self):
        balance = get_balance('mz7poFND7hVGRtPWjiZizcCnjf6wEDWjjT')
        self.assertEquals(balance, 49005500)

    @patch.object(bitcoin.rpc.Proxy, '__init__', mock_init)
    @patch.object(bitcoin.rpc.Proxy, 'listunspent', mock_listunspent_mainnet)
    def test_get_unspent_outputs(self):
        res = get_unspent_outputs('13yNf3azc8sUrjf6UFjUCRZx4B6JnQ4XeJ', 'BTC')
        self.assertIsNotNone(res)
        self.assertTrue(len(res) > 0)

    @patch.object(bitcoin.rpc.Proxy, '__init__', mock_init)
    @patch.object(bitcoin.rpc.Proxy, 'listunspent', mock_listunspent_mainnet)
    def test_get_balance(self):
        balance = get_balance('13yNf3azc8sUrjf6UFjUCRZx4B6JnQ4XeJ', 'BTC')
        self.assertEquals(balance, 81920)


if __name__ == '__main__':
    unittest.main()
