import unittest
import mock
import copy

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV3Handler
from cert_issuer.models import CertificateHandler

presentation_example = {
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://www.blockcerts.org/schema/3.0/context.json"
    ],
    "type": [
        "VerifiablePresentation"
    ],
    "verifiableCredential": [
         {
           "@context": [
             "https://www.w3.org/2018/credentials/v1",
             "https://www.w3.org/2018/credentials/examples/v1",
             "https://www.blockcerts.org/schema/3.0/context.json"
           ],
           "id": "urn:uuid:bbba8553-8ec1-445f-82c9-a57251dd731c",
           "metadataJson": "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{},\"displayOrder\":[\"certificate.issuingInstitution\"]}",
           "displayHtml": "<b>hello world</b>",
           "nonce": "814ce340-12f3-414b-af91-a0f9489e5dbc",
           "universalIdentifier": "ab569127-34bb-5784-bced-00b7e0e82ac9",
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
           },
           "proof": {
             "type": "MerkleProof2019",
             "created": "2020-03-23T15:38:11.804838",
             "proofValue": "z2LuLBVSfnVzaQtvzuA7EaPQsGEgYWeaMTH1p3uqAG3ESx9HYyFzFFrYsyPkZSbn1Ji5LN76jw6HBr3oiaa8KsQenCPqKk7dJvxEXsDnYvhuDHu3ktTZuz4KL2UWU3hieKFwMG2akp4rPvYmwQDbtXNmhZgpdGpp9hiDZiz37bca2LZZG2VJ9Xen31trVG5A2SApCkFoUxYeNvXr8reqJPca1voRwFXAgo25XWV2BQ1ycQ2wM3jPz3BAx4tZuPno7Ebd5XLfroXHCaKiNadiqxLedp2SHZjDicG8kxMwPo2gR1mYeWjtQSPVMrtf6p325wCNVrQpxTAszLp4CPXSZFFYsb2dn9iRAcMTUSKYhYtsNjst2fDdPye4arHmvLL5s6pL6U8vtEEBiYJDrFj8xo",
             "proofPurpose": "assertionMethod",
             "verificationMethod": "ecdsa-koblitz-pubkey:0x7e30a37763e6Ba1fFeDE1750bBeFB4c60b17a1B3"
           }
         }
    ]
}

class TestIssuanceBatchValidation (unittest.TestCase):
    def test_verify_credential_status (self):
        candidate = copy.deepcopy(presentation_example)
        del candidate['verifiableCredential'][0]['credentialSubject']
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
            self.assertEqual(str(e), 'A Verifiable Presentation must contain valid verifiableCredential(s)')
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
