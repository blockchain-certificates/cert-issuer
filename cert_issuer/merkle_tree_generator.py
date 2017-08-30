import hashlib

from chainpoint.chainpoint import MerkleTools

from cert_issuer.helpers import unhexlify


def hash_binary_data(data):
    hashed = hashlib.sha256(data).hexdigest()
    return hashed


class MerkleTreeGenerator(object):
    def __init__(self):
        self.tree = MerkleTools(hash_type='sha256')

    def populate(self, node_generator):
        """
        Populate Merkle Tree with data from node_generator. This requires that node_generator yield elements that
        are binary data. Hashes each and adds it to the Merkle Tree
        :param node_generator:
        :return:
        """
        for binary_data in node_generator:
            hashed = hash_binary_data(binary_data)
            self.tree.add_leaf(hashed, False)

    def get_blockchain_data(self):
        """
        Finalize tree and return binary data to issue on blockchain
        :return:
        """
        self.tree.make_tree()
        return unhexlify(self.tree.get_merkle_root())

    def get_proof_generator(self, tx_id):
        """
        Returns a generator (1-time iterator) of proofs in insertion order.

        :param tx_id: blockchain transaction id
        :return:
        """
        root = self.tree.get_merkle_root()
        node_count = len(self.tree.leaves)
        for index in range(0, node_count):
            proof = self.tree.get_proof(index)
            target_hash = self.tree.get_leaf(index)
            # chainpoint context is causing intermittent SSL errors. This isn't part of the JSON-normalized payload,
            # so we can omit it here
            merkle_proof = {
                # "@context": "https://w3id.org/chainpoint/v2",
                "type": "ChainpointSHA256v2",
                "merkleRoot": root,
                "targetHash": target_hash,
                "proof": proof,
                "anchors": [{
                    "sourceId": tx_id,
                    "type": "BTCOpReturn"
                }]}
            yield merkle_proof
