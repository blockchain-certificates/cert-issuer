import unittest

from cert_issuer.models.verifiable_credential import validate_id


class UnitValidationV3 (unittest.TestCase):
    def test_validate_id_invalid_url(self):
        candidate = 'https:// invalid.url'
        try:
            validate_id(candidate)
        except:
            assert True
            return

        assert False


    def test_validate_issuer_invalid_array(self):
        candidate = [
            "http://example.edu/credentials/3731",
            "http://example.edu/credentials/3732"
        ]
        try:
            validate_id(candidate)
        except Exception as e:
            print(e)
            assert True
            return

        assert False


    def test_validate_issuer_valid_url(self):
        candidate = 'https://valid.url'
        try:
            validate_id(candidate)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()

