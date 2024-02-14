import unittest

from cert_issuer.models import validate_context

class UnitValidationV3 (unittest.TestCase):
    def test_validate_context_invalid_shape (self):
        candidate_context_url = 'https://www.w3.org/2018/credentials/v1'
        candidate_type = ['VerifiableCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert True
            return

        assert False

    def test_validate_context_invalid_order (self):
        candidate_context_url = ['link.to.another.context', 'https://www.w3.org/2018/credentials/v1']
        candidate_type = ['VerifiableCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert True
            return

        assert False

    def test_validate_context_invalid_missing_context (self):
        candidate_context_url = ['https://www.w3.org/2018/credentials/v1']
        candidate_type = ['VerifiableCredential', 'BlockcertsCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert True
            return

        assert False

    def test_validate_context_no_duplicate_vc_context (self):
        candidate_context_url = [
            'https://www.w3.org/2018/credentials/v1',
            'https://www.w3.org/ns/credentials/v2',
            'https://w3id.org/blockcerts/v3'
        ]
        candidate_type = ['VerifiableCredential', 'BlockcertsCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert True
            return

        assert False

    def test_validate_context_valid_w3idcanon (self):
        candidate_context_url = ['https://www.w3.org/2018/credentials/v1', 'https://w3id.org/blockcerts/v3']
        candidate_type = ['VerifiableCredential', 'BlockcertsCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert False
            return

        assert True

    def test_validate_context_valid_v2_w3idcanon (self):
        candidate_context_url = ['https://www.w3.org/ns/credentials/v2', 'https://w3id.org/blockcerts/v3']
        candidate_type = ['VerifiableCredential', 'BlockcertsCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert False
            return

        assert True

    def test_validate_context_valid_blockcerts (self):
        candidate_context_url = ['https://www.w3.org/2018/credentials/v1', 'https://www.blockcerts.org/schema/3.0/context.json']
        candidate_type = ['VerifiableCredential', 'BlockcertsCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
