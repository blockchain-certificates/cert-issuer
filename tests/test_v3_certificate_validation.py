import unittest
import mock
import copy

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV3Handler
from cert_issuer.models import CertificateHandler

credential_example = {
   "@context": [
     "https://www.w3.org/2018/credentials/v1",
     "https://www.blockcerts.org/schema/3.0-alpha/context.json",
     "https://www.w3.org/2018/credentials/examples/v1"
   ],
   "id": "urn:uuid:bbba8553-8ec1-445f-82c9-a57251dd731c",
   "type": [
     "VerifiableCredential",
     "BlockcertsCredential"
   ],
   "issuer": "https://raw.githubusercontent.com/AnthonyRonning/https-github.com-labnol-files/master/issuer-eth.json",
   "issuanceDate": "2010-01-01T19:33:24Z",
   "credentialSubject": {
     "id": "did:key:z6Mkq3L1jEDDZ5R7eT523FMLxC4k6MCpzqD7ff1CrkWpoJwM",
     "alumniOf": {
       "id": "did:example:c276e12ec21ebfeb1f712ebc6f1"
     }
   }
}

class TestCertificateV3Validation(unittest.TestCase):
    def missing_credential_subject (self):
        candidate = copy.deepcopy(credential_example)
        del candidate['credentialSubject']
        handler.certificates_to_issue = [mock.Mock()]
        handler = CertificateBatchHandler(
            secret_manager=mock.Mock(),
            certificate_handler=MockCertificateV3Handler(candidate),
            merkle_tree=mock.Mock(),
            config=mock.Mock()
        )

        try:
            handler.prepare_batch()
        except:
            assert False
            return

        assert True

class MockCertificateV3Handler(CertificateV3Handler):
    def __init__(self, test_certificate):
        raise ValueError('mock init');
        self.test_certificate = test_certificate
    def _get_certificate_to_issue(data):
        print('mock call')
        return self.test_certificate

if __name__ == '__main__':
    unittest.main()
