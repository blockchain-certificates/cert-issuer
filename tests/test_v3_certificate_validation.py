import unittest

import mock
import json
import io
from pycoin.serialize import b2h
from mock import patch, mock_open

from cert_issuer.certificate_handlers import CertificateWebV3Handler, CertificateV3Handler, CertificateBatchHandler, CertificateHandler, CertificateBatchWebHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer import helpers
from cert_core import Chain
from mock import ANY

class TestV3CertificateValidation(unittest.TestCase):
    def _proof_helper(self, chain):
        proof = {
                    'type': 'MerkleProof2019',
                    'created': ANY,
                    'proofValue': ANY,
                    'proofPurpose': 'assertionMethod',
                    'verificationMethod': ANY
                }
        return proof

    def _helper_mock_call(self, *args):
        helper_mock = mock.MagicMock()
        helper_mock.__len__.return_value = self.directory_count

        assert args == (
            '/unsigned_certificates_dir',
            '/signed_certificates_dir',
            '/blockchain_certificates_dir',
            '/work_dir')
        
        return helper_mock

    def _get_certificate_batch_web_handler(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        config = mock.Mock()
        config.issuing_address = "http://example.com"

        handler = CertificateBatchWebHandler(
                secret_manager=secret_manager,
                certificate_handler=DummyCertificateHandler(),
                merkle_tree=MerkleTreeGenerator(),
                config=config)

        return handler, certificates_to_issue

    def _get_certificate_batch_handler(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        config = mock.Mock()
        config.issuing_address = "http://example.com"

        handler = CertificateBatchHandler(
                secret_manager=secret_manager,
                certificate_handler=DummyCertificateHandler(),
                merkle_tree=MerkleTreeGenerator(),
                config=config)

        return handler, certificates_to_issue

    def test_validate_type_valid(self):
        certificate = {
            'type': ['VerifiableCredential', 'VerifiablePresentation']
        }

class DummyCertificateHandler(CertificateHandler):
    def __init__(self):
        self.config = mock.Mock()
        self.config.issuing_address = "http://example.com"
        self.counter = 0

    def _get_certificate_to_issue (self, certificate_metadata):
        pass

    def validate_certificate(self, certificate_metadata):
        pass

    def sign_certificate(self, signer, certificate_metadata):
        pass

    def get_byte_array_to_issue(self, certificate_metadata):
        self.counter += 1
        return str(self.counter).encode('utf-8')

    def add_proof(self, certificate_metadata, merkle_proof):
        pass


if __name__ == '__main__':
    unittest.main()
