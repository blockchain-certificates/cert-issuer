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

    def test_validate_context_valid (self):
        candidate_context_url = ['https://www.w3.org/2018/credentials/v1', 'https://www.w3id.org/blockcerts/v3.0-alpha']
        candidate_type = ['VerifiableCredential', 'BlockcertsCredential']
        try:
            validate_context(candidate_context_url, candidate_type)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
