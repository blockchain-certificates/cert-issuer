import unittest

from cert_core import Chain
from pycoin.serialize import b2h

from cert_issuer.merkle_tree_generator import MerkleTreeGenerator


def get_test_data_generator():
    """
    Returns a generator (1-time iterator) of test data
    :return:
    """
    for num in range(1, 4):
        yield str(num).encode('utf-8')


class TestMerkleTreeGenerator(unittest.TestCase):
    def test_generate(self):
        merkle_tree_generator = MerkleTreeGenerator()
        merkle_tree_generator.populate(get_test_data_generator())
        byte_array = merkle_tree_generator.get_blockchain_data()
        self.assertEqual(b2h(byte_array), '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044')

    def test_proofs_bitcoin_mainnet(self):
        self.do_test_signature(Chain.bitcoin_mainnet, 'bitcoinMainnet', 'BTCOpReturn')

    def test_proofs_bitcoin_testnet(self):
        self.do_test_signature(Chain.bitcoin_testnet, 'bitcoinTestnet', 'BTCOpReturn')

    def test_proofs_bitcoin_regtest(self):
        self.do_test_signature(Chain.bitcoin_regtest, 'bitcoinRegtest', 'BTCOpReturn')

    def test_proofs_mock(self):
        self.do_test_signature(Chain.mockchain, 'mockchain', 'Mock')

    def do_test_signature(self, chain, display_chain, type):
        merkle_tree_generator = MerkleTreeGenerator()
        merkle_tree_generator.populate(get_test_data_generator())
        _ = merkle_tree_generator.get_blockchain_data()
        gen = merkle_tree_generator.get_proof_generator(
            '8087c03e7b7bc9ca7b355de9d9d8165cc5c76307f337f0deb8a204d002c8e582', chain)
        p1 = next(gen)
        _ = next(gen)
        p3 = next(gen)
        p1_expected = {'type': ['MerkleProof2017', 'Extension'],
                       'merkleRoot': '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044',
                       'targetHash': '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
                       'proof': [{'right': 'd4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35'},
                                 {'right': '4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce'}],
                       'anchors': [
                           {'sourceId': '8087c03e7b7bc9ca7b355de9d9d8165cc5c76307f337f0deb8a204d002c8e582',
                            'type': type,
                            'chain': display_chain}]}
        p3_expected = {'type': ['MerkleProof2017', 'Extension'],
                       'merkleRoot': '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044',
                       'targetHash': '4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce',
                       'proof': [{'left': '4295f72eeb1e3507b8461e240e3b8d18c1e7bd2f1122b11fc9ec40a65894031a'}],
                       'anchors': [{'sourceId': '8087c03e7b7bc9ca7b355de9d9d8165cc5c76307f337f0deb8a204d002c8e582',
                                    'type': type,
                                    'chain': display_chain}]}
        self.assertEqual(p1, p1_expected)
        self.assertEqual(p3, p3_expected)


if __name__ == '__main__':
    unittest.main()
