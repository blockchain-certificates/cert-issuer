import unittest

import mock

from cert_issuer.certificate_handler import CertificateBatchHandler, CertificateHandler
from cert_issuer.helpers import hexlify


class TestCertificateHandler(unittest.TestCase):
    def test_prepare_batch(self):
        secret_manager = mock.Mock()
        certificates_to_issue = dict()
        certificates_to_issue['1'] = mock.Mock()
        certificates_to_issue['2'] = mock.Mock()
        certificates_to_issue['3'] = mock.Mock()

        certificate_batch_handler = CertificateBatchHandler(secret_manager=secret_manager,
                                                            certificate_handler=DummyCertificateHandler())
        certificate_batch_handler.set_certificates_in_batch(certificates_to_issue)
        result = certificate_batch_handler.prepare_batch()
        self.assertEqual(hexlify(result), '0932f1d2e98219f7d7452801e2b64ebd9e5c005539db12d9b1ddabe7834d9044')


class DummyCertificateHandler(CertificateHandler):
    def __init__(self):
        self.counter = 0

    def validate_certificate(self, certificate_metadata):
        pass

    def sign_certificate(self, signer, certificate_metadata):
        pass

    def get_data_to_issue(self, certificate_metadata):
        self.counter += 1
        return str(self.counter).encode()

    def add_proof(self, certificate_metadata, merkle_proof):
        pass


if __name__ == '__main__':
    unittest.main()
