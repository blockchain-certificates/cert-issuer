import json
import logging

from cert_schema import normalize_jsonld
from cert_schema import validate_v2
from pycoin.serialize import b2h

from cert_issuer.models import CertificateHandler
from cert_issuer.signer import FinalizableSigner


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

    def get_byte_array_to_issue(self, certificate_metadata):
        certificate_json = self._get_certificate_to_issue(certificate_metadata)
        normalized = normalize_jsonld(certificate_json, detect_unmapped_fields=False)
        return normalized.encode('utf-8')

    def add_proof(self, certificate_metadata, merkle_proof):
        """
        :param certificate_metadata:
        :param merkle_proof:
        :return:
        """
        certificate_json = self._get_certificate_to_issue(certificate_metadata)
        certificate_json['signature'] = merkle_proof

        with open(certificate_metadata.blockchain_cert_file_name, 'w') as out_file:
            out_file.write(json.dumps(certificate_json))

    def _get_certificate_to_issue(self, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name, 'r') as unsigned_cert_file:
            certificate_json = json.load(unsigned_cert_file)
        return certificate_json


class CertificateBatchHandler(object):
    """
    Manages a batch of certificates. Responsible for iterating certificates in a consistent order.

    In this case, certificates are initialized as an Ordered Dictionary, and we iterate in insertion order.
    """

    def __init__(self, secret_manager, certificate_handler, merkle_tree):
        self.certificate_handler = certificate_handler
        self.secret_manager = secret_manager
        self.merkle_tree = merkle_tree

    def set_certificates_in_batch(self, certificates_to_issue):
        self.certificates_to_issue = certificates_to_issue

    def prepare_batch(self):
        """
        Propagates exception on failure
        :return: byte array to put on the blockchain
        """

        # validate batch
        for _, metadata in self.certificates_to_issue.items():
            self.certificate_handler.validate_certificate(metadata)

        # sign batch
        with FinalizableSigner(self.secret_manager) as signer:
            for _, metadata in self.certificates_to_issue.items():
                self.certificate_handler.sign_certificate(signer, metadata)

        self.merkle_tree.populate(self.get_certificate_generator())
        logging.info('here is the op_return_code data: %s', b2h(self.merkle_tree.get_blockchain_data()))
        return self.merkle_tree.get_blockchain_data()

    def get_certificate_generator(self):
        """
        Returns a generator (1-time iterator) of certificates in the batch
        :return:
        """
        for uid, metadata in self.certificates_to_issue.items():
            data_to_issue = self.certificate_handler.get_byte_array_to_issue(metadata)
            yield data_to_issue

    def finish_batch(self, tx_id, chain):
        proof_generator = self.merkle_tree.get_proof_generator(tx_id, chain)
        for uid, metadata in self.certificates_to_issue.items():
            proof = next(proof_generator)
            self.certificate_handler.add_proof(metadata, proof)
