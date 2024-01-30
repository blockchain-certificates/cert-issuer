import unittest
import mock
import copy

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV3Handler

credential_example = {
   "@context": [
     "https://www.w3.org/2018/credentials/v1",
     "https://www.w3.org/2018/credentials/examples/v1",
     "https://www.blockcerts.org/schema/3.0/context.json"
   ],
   "id": "urn:uuid:bbba8553-8ec1-445f-82c9-a57251dd731c",
   "type": [
     "VerifiableCredential",
     "BlockcertsCredential"
   ],
   "issuer": "https://raw.githubusercontent.com/AnthonyRonning/https-github.com-labnol-files/master/issuer-eth.json",
   "issuanceDate": "2024-01-01T19:33:24Z",
   "credentialSubject": {
     "id": "did:key:z6Mkq3L1jEDDZ5R7eT523FMLxC4k6MCpzqD7ff1CrkWpoJwM",
     "alumniOf": {
       "id": "did:example:c276e12ec21ebfeb1f712ebc6f1"
     }
   }
}

class TestIssuanceBatchValidation (unittest.TestCase):
    def test_verify_type (self):
        candidate = copy.deepcopy(credential_example)
        candidate['type'] = 'Invalid Shape'
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
            self.assertEqual(str(e), '`type` property must be an array')
            return

        assert False

    def test_verify_context (self):
        candidate = copy.deepcopy(credential_example)
        candidate['@context'] = 'Invalid Shape'
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
            self.assertEqual(str(e), '`@context` property must be an array')
            return

        assert False

    def test_verify_credential_subject (self):
        candidate = copy.deepcopy(credential_example)
        del candidate['credentialSubject']
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
            self.assertEqual(str(e), '`credentialSubject` property must be defined')
            return

        assert False

    def test_verify_issuer (self):
        candidate = copy.deepcopy(credential_example)
        del candidate['issuer']
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
            self.assertEqual(str(e), '`issuer` property must be defined')
            return

        assert False

    def test_verify_issuance_date (self):
        candidate = copy.deepcopy(credential_example)
        del candidate['issuanceDate']
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
            self.assertEqual(str(e), '`issuanceDate` property must be defined')
            return

        assert False

    def test_verify_expiration_date (self):
        candidate = copy.deepcopy(credential_example)
        candidate['expirationDate'] = '20200909'
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
            self.assertEqual(str(e), '`expirationDate` property must be a valid RFC3339 string. Value received: `20200909`')
            return

        assert False

    def test_verify_expiration_date_before_issuance_date_invalid (self):
        candidate = copy.deepcopy(credential_example)
        candidate['expirationDate'] = '2023-01-01T19:33:24Z'
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
            self.assertEqual(str(e), '`expirationDate` property must be a date set after `issuanceDate`')
            return

        assert False

    def test_verify_credential_status (self):
        candidate = copy.deepcopy(credential_example)
        candidate['credentialStatus'] = {
            "id": 'https://valid.path'
        }
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
            self.assertEqual(str(e), 'credentialStatus.type must be defined')
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
