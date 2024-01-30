import unittest
import mock
import copy

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV3Handler

credential_example = {
   "@context": [
     "https://www.w3.org/ns/credentials/v2",
     "https://www.blockcerts.org/schema/3.0/context.json"
   ],
   "id": "urn:uuid:bbba8553-8ec1-445f-82c9-a57251dd731c",
   "type": [
     "VerifiableCredential",
     "BlockcertsCredential"
   ],
   "issuer": "https://raw.githubusercontent.com/AnthonyRonning/https-github.com-labnol-files/master/issuer-eth.json",
   "validFrom": "2024-01-29T19:33:24Z",
   "credentialSubject": {
     "id": "did:key:z6Mkq3L1jEDDZ5R7eT523FMLxC4k6MCpzqD7ff1CrkWpoJwM",
   }
}

class TestIssuanceBatchValidation (unittest.TestCase):
    def test_verify_valid_from (self):
        candidate = copy.deepcopy(credential_example)
        candidate['validFrom'] = '20240130'
        handler = CertificateBatchHandler(
            secret_manager=mock.Mock(),
            certificate_handler=MockCertificateV3Handler(candidate),
            merkle_tree=mock.Mock(),
            config=mock.Mock()
        )
        handler.certificates_to_issue = {'metadata': mock.Mock()}

        try:
            handler.prepare_batch()
        except Exception as e:
            self.assertEqual(str(e), '`validFrom` property must be a valid RFC3339 string. Value received: `20240130`')
            return

        assert False

    def test_verify_valid_until (self):
        candidate = copy.deepcopy(credential_example)
        candidate['validUntil'] = '20200909'
        handler = CertificateBatchHandler(
            secret_manager=mock.Mock(),
            certificate_handler=MockCertificateV3Handler(candidate),
            merkle_tree=mock.Mock(),
            config=mock.Mock()
        )
        handler.certificates_to_issue = {'metadata': mock.Mock()}

        try:
            handler.prepare_batch()
        except Exception as e:
            self.assertEqual(str(e), '`validUntil` property must be a valid RFC3339 string. Value received: `20200909`')
            return

        assert False

    def test_verify_valid_until_before_validFrom_invalid (self):
        candidate = copy.deepcopy(credential_example)
        candidate['validUntil'] = '2024-01-01T19:33:24Z'
        handler = CertificateBatchHandler(
            secret_manager=mock.Mock(),
            certificate_handler=MockCertificateV3Handler(candidate),
            merkle_tree=mock.Mock(),
            config=mock.Mock()
        )
        handler.certificates_to_issue = {'metadata': mock.Mock()}

        try:
            handler.prepare_batch()
        except Exception as e:
            self.assertEqual(str(e), '`validUntil` property must be a date set after `validFrom`')
            return

        assert False

class MockCertificateV3Handler(CertificateV3Handler):
    def __init__(self, test_certificate):
        self.test_certificate = test_certificate
        print(self.test_certificate)
    def _get_certificate_to_issue(self, data):
        return self.test_certificate

if __name__ == '__main__':
    unittest.main()
