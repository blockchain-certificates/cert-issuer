import unittest
import copy

from cert_issuer.models import verify_credential

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
   },
   "proof": {
     "type": "MerkleProof2019",
     "created": "2020-03-11T09:48:20.304161",
     "proofValue": "z2LuLBVSfnVzaQtvzuA7EaPQsGEgYWeaMTH1p3uqAG3ESx9HYyFzFFrYsyPkZSbn1Ji5LN76jw6HBr3oiaa8KsQenCPqKk7dJvxEXsDnYvhuDHtsDaQdmCyvpTR9oH46UZcCZ1UY7uZrgHmzf3J8Mzpp5Nnzd4SWiVN4RDWfxSkKmcoXywZ1pTm5bhbKAx1Xeydjwf7T7gcSSkUxQJmfJrWKdyiBjU1vt4oZxwbeTRQ9TfojiDRKJ6RPNsVPpkcDqGvPoaF58SQJG9xr8ACAAH9ZhYXJhRwW2zLpHGdRgyFGdxrcNiBVJ1o1TLcwLsfXTdRZLV2gW5yPLbEui6yBsmHtw9pQkWtfMxGBLzHk5ZRVLMdgUKatiV2QS4oE9N2GyiVnmQomApdS8R2cDSbQdn",
     "proofPurpose": "assertionMethod",
     "verificationMethod": "ecdsa-koblitz-pubkey:0x7e30a37763e6Ba1fFeDE1750bBeFB4c60b17a1B3"
   }
}

class UnitValidationV3 (unittest.TestCase):
    def test_verify_credential_missing_credentialSubject (self):
        candidate = copy.deepcopy(credential_example)
        del candidate['credentialSubject']
        try:
            verify_credential(candidate)
        except:
            assert True
            return

        assert False

    def test_verify_credential_missing_issuer (self):
        candidate = copy.deepcopy(credential_example)
        del candidate['issuer']
        try:
            verify_credential(candidate)
        except:
            assert True
            return

        assert False

    def test_verify_credential_invalid_issuer (self):
        candidate = copy.deepcopy(credential_example)
        candidate['issuer'] = 'not a url'
        try:
            verify_credential(candidate)
        except:
            assert True
            return

        assert False

    def test_verify_credential_missing_issuance_date (self):
        candidate = copy.deepcopy(credential_example)
        del candidate['issuanceDate']
        try:
            verify_credential(candidate)
        except:
            assert True
            return

        assert False

    def test_verify_credential_invalid_issuance_date (self):
        candidate = copy.deepcopy(credential_example)
        candidate['issuanceDate'] = '20200202'
        try:
            verify_credential(candidate)
        except:
            assert True
            return

        assert False

    def test_verify_credential_missing_optional_expiration_date (self):
        candidate = copy.deepcopy(credential_example)
        try:
            verify_credential(candidate)
        except:
            assert False
            return

        assert True

    def test_verify_credential_invalid_expiration_date (self):
        candidate = copy.deepcopy(credential_example)
        candidate['expirationDate'] = '20200202'
        try:
            verify_credential(candidate)
        except:
            assert True
            return

        assert False

    def test_verify_credential_valid_expiration_date (self):
        candidate = copy.deepcopy(credential_example)
        candidate['expirationDate'] = '2020-02-02T00:00:00Z'
        try:
            verify_credential(candidate)
        except:
            assert False
            return

        assert True

    def test_verify_credential_missing_optional_credential_status (self):
        candidate = copy.deepcopy(credential_example)
        try:
            verify_credential(candidate)
        except:
            assert False
            return

        assert True

    def test_verify_credential_invalid_credential_status (self):
        candidate = copy.deepcopy(credential_example)
        candidate['credentialStatus'] = {
            'invalid': True
        }
        try:
            verify_credential(candidate)
        except:
            assert True
            return

        assert False

    def test_verify_credential_valid_credential_status (self):
        candidate = copy.deepcopy(credential_example)
        candidate['credentialStatus'] = {
            'id': 'https://valid.path',
            'type': 'statusList'
        }
        try:
            verify_credential(candidate)
        except:
            assert False
            return

        assert True

    def test_verify_credential_valid (self):
        candidate = copy.deepcopy(credential_example)
        try:
            verify_credential(candidate)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
