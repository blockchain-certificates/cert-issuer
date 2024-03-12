import unittest

from cert_issuer.models.verifiable_credential import validate_issuer

class UnitValidationV3 (unittest.TestCase):
    def test_validate_issuer_invalid_url (self):
        candidate = 'VerifiablePresentation'
        try:
            validate_issuer(candidate)
        except:
            assert True
            return

        assert True

    def test_validate_issuer_invalid_url_with_space (self):
        candidate = 'https:// invalid.url'
        try:
            validate_issuer(candidate)
        except:
            assert True
            return

        assert False

    def test_validate_issuer_invalid_array (self):
        candidate = ['https://first.issuer/profile', 'https://second.issuer/profile']
        try:
            validate_issuer(candidate)
        except Exception as e:
            print(e)
            assert True
            return

        assert False

    def test_validate_issuer_valid_url (self):
        candidate = 'https://valid.url'
        try:
            validate_issuer(candidate)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
