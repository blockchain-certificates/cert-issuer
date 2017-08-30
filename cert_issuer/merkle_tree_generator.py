import hashlib

from chainpoint.chainpoint import MerkleTools


def hash_binary_data(data):
    hashed = hashlib.sha256(data).hexdigest()
    return hashed


def ensure_string(str_value):
    if isinstance(str_value, str):
        return str_value
    return str_value.decode('utf-8')


class MerkleTreeGenerator(object):
    def __init__(self):
        self.tree = MerkleTools(hash_type='sha256')

    def populate(self, node_generator):
        """
        Populate Merkle Tree with data from node_generator. This requires that node_generator yield string elements.
        Adds it to the Merkle Tree (which hashes and hex encodes via the second True parameter)
        :param node_generator:
        :return:
        """
        for data in node_generator:
            self.tree.add_leaf(data, True)

    def get_blockchain_data(self):
        """
        Finalize tree and return hex string to issue on blockchain
        :return:
        """
        self.tree.make_tree()
        merkle_root = self.tree.get_merkle_root()
        return ensure_string(merkle_root)

    def get_proof_generator(self, tx_id):
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
            # chainpoint context is causing intermittent SSL errors. This isn't part of the JSON-normalized payload,
            # so we can omit it here
            merkle_proof = {
                # "@context": "https://w3id.org/chainpoint/v2",
                "type": "ChainpointSHA256v2",
                "merkleRoot": root,
                "targetHash": target_hash,
                "proof": proof2,
                "anchors": [{
                    "sourceId": tx_id,
                    "type": "BTCOpReturn"
                }]}
            yield merkle_proof
