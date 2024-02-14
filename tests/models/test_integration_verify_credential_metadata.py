import unittest
import mock

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
   "issuanceDate": "2010-01-01T19:33:24Z",
   "metadata": "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{},\"displayOrder\":{\"certificate.issuingInstitution\":1}}",
   "credentialSubject": {
     "id": "did:key:z6Mkq3L1jEDDZ5R7eT523FMLxC4k6MCpzqD7ff1CrkWpoJwM",
     "alumniOf": {
       "id": "did:example:c276e12ec21ebfeb1f712ebc6f1"
     }
   }
}

class TestIntegrationCredentialMetadata (unittest.TestCase):
    def test_verify_metadata_invalid (self):
        handler = CertificateBatchHandler(
            secret_manager=mock.Mock(),
            certificate_handler=MockCertificateV3Handler(credential_example),
            merkle_tree=mock.Mock(),
            config=mock.Mock()
        )
        handler.certificates_to_issue = {'metadata': mock.Mock()}

        try:
            handler.prepare_batch()
        except Exception as e:
            self.assertEqual(str(e), 'Certificate.metadata object does not match its provided schema')
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