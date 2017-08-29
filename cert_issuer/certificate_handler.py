import hashlib
import json
from abc import abstractmethod

from cert_schema import normalize_jsonld
from cert_schema import validate_v2
from chainpoint.chainpoint import MerkleTools

from cert_issuer.helpers import unhexlify
from cert_issuer.signer import FinalizableSigner


def hash_normalized_jsonld(normalized):
    """
    Hash the JSON-LD normalized certificate
    :param certificate:
    :return:
    """
    hashed = hashlib.sha256(bytes(normalized, 'utf-8')).hexdigest()
    return hashed


def hash_binary_data(data):
    hashed = hashlib.sha256(data).hexdigest()
    return hashed


class CertificateBatchHandler(object):
    """
    Manages a batch of certificates. Responsible for iterating certificates in a consistent order.

    In this case, certificates are initialized as an Ordered Dictionary, and we iterate in insertion order.
    """

    def __init__(self, secret_manager, certificate_handler=CertificateV2Handler()):
        self.certificate_handler = certificate_handler
        self.secret_manager = secret_manager
        self.tree = MerkleTools(hash_type='sha256')
        self.certificates_to_issue = None

    def prepare_batch(self):
        """
        Propagates exception on failure
        :return:
        """

        # validate batch
        for _, metadata in self.certificates_to_issue.items():
            self.certificate_handler.validate_certificate(metadata)

        # sign batch
        with FinalizableSigner(self.secret_manager) as signer:
            for _, metadata in self.certificates_to_issue.items():
                self.certificate_handler.sign_certificate(signer, metadata)

        node_generator = self.create_node_generator()
        for node in node_generator:
            self.tree.add_leaf(node, False)

        self.tree.make_tree()
        return unhexlify(self.tree.get_merkle_root())  # bytes

    def create_node_generator(self):
        for uid, metadata in self.certificates_to_issue.items():
            binary_data = self.certificate_handler.get_data_to_issue(metadata)
            hashed = hash_binary_data(binary_data)
            yield hashed

    def finish_batch(self, tx_id):
        def create_proof_generator(tree):
            root = tree.get_merkle_root()
            node_count = len(tree.leaves)
            for index in range(0, node_count):
                proof = tree.get_proof(index)
                target_hash = tree.get_leaf(index)
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

        self.add_proofs(create_proof_generator, self.tree)

    def add_proofs(self, generator):
        gen = generator(self.tree)
        for uid, metadata in self.certificates_to_issue.items():
            merkle_proof = next(gen)
            self.certificate_handler.add_proof(metadata, merkle_proof)


class CertificateHandler(object):
    @abstractmethod
    def validate_certificate(self, certificate_metadata):
        pass

    @abstractmethod
    def sign_certificate(self, signer, certificate_metadata):
        pass

    @abstractmethod
    def get_data_to_issue(self, certificate_metadata):
        pass

    @abstractmethod
    def add_proof(self, certificate_metadata, merkle_proof):
        pass


class CertificateV2Handler(CertificateHandler):
    def validate_certificate(self, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name) as cert:
            certificate_json = json.load(cert)
            # Both tests raise exception on failure
            # 1. json schema validation
            validate_v2(certificate_json)
            # 2. detect if there are any unmapped fields
            normalize_jsonld(certificate_json, detect_unmapped_fields=True)

    def sign_certificate(self, signer, certificate_metadata):
        pass

    def get_data_to_issue(self, certificate_metadata):
        certificate_json = self._get_certificate_to_issue(certificate_metadata)
        normalized = normalize_jsonld(certificate_json, detect_unmapped_fields=False)
        binary_data = bytes(normalized, 'utf-8')
        return binary_data

    def add_proof(self, certificate_metadata, merkle_proof):
        """
        :param certificate_metadata:
        :param merkle_proof:
        :return:
        """
        certificate_json = self._get_certificate_to_issue(certificate_metadata)

        merkle_proof['type'] = ['MerkleProof2017', 'Extension']
        certificate_json['signature'] = merkle_proof

        with open(certificate_metadata.blockchain_cert_file_name, 'w') as out_file:
            out_file.write(json.dumps(certificate_json))

    def _get_certificate_to_issue(self, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name, 'r') as unsigned_cert_file:
            certificate_json = json.load(unsigned_cert_file)
        return certificate_json
