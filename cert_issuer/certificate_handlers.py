import json
import logging

from cert_issuer import helpers
from cert_issuer.proof_handler import ProofHandler
from pycoin.serialize import b2h
from cert_issuer.normalization_handler import JSONLDHandler
from cert_issuer.models import CertificateHandler, BatchHandler

from cert_issuer.signer import FinalizableSigner


class CertificateV3Handler(CertificateHandler):
    def __init__(self, app_config):
        self.app_config = app_config

    def get_byte_array_to_issue(self, certificate_metadata):
        certificate_json = self._get_certificate_to_issue(certificate_metadata)
        return JSONLDHandler.normalize_to_utf8(certificate_json)

    def add_proof(self, certificate_metadata, merkle_proof):
        """
        :param certificate_metadata:
        :param merkle_proof:
        :return:
        """
        certificate_json = self._get_certificate_to_issue(certificate_metadata)
        certificate_json = ProofHandler().add_proof(certificate_json, merkle_proof, self.app_config)

        with open(certificate_metadata.blockchain_cert_file_name, 'w') as out_file:
            out_file.write(json.dumps(certificate_json))

    def _get_certificate_to_issue(self, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name, 'r') as unsigned_cert_file:
            certificate_json = json.load(unsigned_cert_file)
        return certificate_json

class CertificateWebV3Handler(CertificateHandler):
    def __init__(self, app_config):
        self.app_config = app_config

    def get_byte_array_to_issue(self, certificate_json):
        return JSONLDHandler.normalize_to_utf8(certificate_json)

    def add_proof(self, certificate_json, merkle_proof):
        certificate_json = ProofHandler().add_proof(certificate_json, merkle_proof, self.app_config)
        return certificate_json

class CertificateBatchWebHandler(BatchHandler):
    def finish_batch(self, tx_id, chain):
        self.proof = []
        proof_generator = self.merkle_tree.get_proof_generator(tx_id, self.config.verification_method, chain)
        for metadata in self.certificates_to_issue:
            proof = next(proof_generator)
            self.proof.append(self.certificate_handler.add_proof(metadata, proof))

    def get_certificate_generator(self):
        """
        Returns a generator (1-time iterator) of certificates in the batch
        :return:
        """

        for cert in self.certificates_to_issue:
            data_to_issue = self.certificate_handler.get_byte_array_to_issue(cert)
            yield data_to_issue

    def prepare_batch(self):
        """
        Propagates exception on failure
        :return: byte array to put on the blockchain
        """

        for cert in self.certificates_to_issue:
            self.certificate_handler.validate_certificate(cert)

        self.merkle_tree.populate(self.get_certificate_generator())
        logging.info('here is the op_return_code data: %s', b2h(self.merkle_tree.get_blockchain_data()))
        return self.merkle_tree.get_blockchain_data()


class CertificateBatchHandler(BatchHandler):
    """
    Manages a batch of certificates. Responsible for iterating certificates in a consistent order.

    In this case, certificates are initialized as an Ordered Dictionary, and we iterate in insertion order.
    """
    def pre_batch_actions(self, config):
        self._process_directories(config)

    def post_batch_actions(self, config):
        helpers.copy_output(self.certificates_to_issue)
        logging.info('Your Blockchain Certificates are in %s', config.blockchain_certificates_dir)

    def prepare_batch(self):
        """
        Propagates exception on failure
        :return: byte array to put on the blockchain
        """

        # validate batch
        for _, metadata in self.certificates_to_issue.items():
            certificate_json = self.certificate_handler._get_certificate_to_issue(metadata)
            self.certificate_handler.validate_certificate(certificate_json)

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
        proof_generator = self.merkle_tree.get_proof_generator(tx_id, self.config.verification_method, chain)
        for _, metadata in self.certificates_to_issue.items():
            proof = next(proof_generator)
            self.certificate_handler.add_proof(metadata, proof)

    def _process_directories(self, config):
        unsigned_certs_dir = config.unsigned_certificates_dir
        signed_certs_dir = config.signed_certificates_dir
        blockchain_certificates_dir = config.blockchain_certificates_dir
        work_dir = config.work_dir

        certificates_metadata = helpers.prepare_issuance_batch(
                unsigned_certs_dir,
                signed_certs_dir,
                blockchain_certificates_dir,
                work_dir)

        num_certificates = len(certificates_metadata)

        if num_certificates < 1:
            return None

        logging.info('Processing %d certificates under work path=%s', num_certificates, work_dir)
        self.set_certificates_in_batch(certificates_metadata)

