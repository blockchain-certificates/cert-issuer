import hashlib
import logging
from datetime import datetime

from cert_core import Chain
from blockcerts_merkletools import MerkleTools
from pycoin.encoding.hexbytes import h2b
from lds_merkle_proof_2019.merkle_proof_2019 import MerkleProof2019
from cert_issuer import helpers


def hash_byte_array(data):
    hashed = hashlib.sha256(data).hexdigest()
    return hashed


def ensure_string(value):
    if isinstance(value, str):
        return value
    return value.decode('utf-8')


class MerkleTreeGenerator(object):
    def __init__(self):
        self.tree = MerkleTools(hash_type='sha256')

    def populate(self, node_generator):
        """
        Populate Merkle Tree with data from node_generator. This requires that node_generator yield byte[] elements.
        Hashes, computes hex digest, and adds it to the Merkle Tree
        :param node_generator:
        :return:
        """
        for data in node_generator:
            hashed = hash_byte_array(data)
            self.tree.add_leaf(hashed)

    def get_blockchain_data(self):
        """
        Finalize tree and return byte array to issue on blockchain
        :return:
        """
        self.tree.make_tree()
        merkle_root = self.tree.get_merkle_root()
        return h2b(ensure_string(merkle_root))

    def get_proof_generator(self, tx_id, chain=Chain.bitcoin_mainnet):
        """
        Returns a generator (1-time iterator) of proofs in insertion order.

        :param tx_id: blockchain transaction id
        :return:
        """
        root = ensure_string(self.tree.get_merkle_root())
        node_count = len(self.tree.leaves)
        for index in range(0, node_count):
            proof = self.tree.get_proof(index)
            proof2 = []

            for p in proof:
                dict2 = dict()
                for key, value in p.items():
                    dict2[key] = ensure_string(value)
                proof2.append(dict2)
            target_hash = ensure_string(self.tree.get_leaf(index))
            mp2019 = MerkleProof2019()
            merkle_json = {
                  "path": proof2,
                  "merkleRoot": root,
                  "targetHash": target_hash,
                  "anchors": [
                    helpers.tx_to_blink(chain, tx_id)
                  ]
                }
            logging.info('merkle_json: %s', str(merkle_json))

            proof_value = mp2019.encode(merkle_json)
            yield proof_value


def to_source_id(txid, chain):
    if chain.is_bitcoin_type() or chain.is_ethereum_type():
        return txid
    else:
        return 'This has not been issued on a blockchain and is for testing only'
