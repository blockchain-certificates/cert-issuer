import unittest

import mock
from pycoin.serialize import b2h

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator


class TestCertificateHandler(unittest.TestCase):
    def test_prepare_batch(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        certificate_batch_handler = CertificateBatchHandler(secret_manager=secret_manager,
                                                            certificate_handler=DummyCertificateHandler(),
                                                            merkle_tree=MerkleTreeGenerator())
        certificate_batch_handler.set_certificates_in_batch(certificates_to_issue)
        result = certificate_batch_handler.prepare_batch()
        self.assertEqual(b2h(result), '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044')


class DummyCertificateHandler(CertificateHandler):
    def __init__(self):
        self.counter = 0

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
