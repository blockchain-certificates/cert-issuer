import unittest

from cert_issuer.models.verifiable_credential import validate_expiration_date

class UnitValidationV3 (unittest.TestCase):
    def test_validate_expiration_date_invalid_RFC3339 (self):
        candidate = '20200202'
        try:
            validate_expiration_date(candidate)
        except:
            assert True
            return

        assert False

    def test_validate_expiration_date_valid_RFC3339 (self):
        candidate = '2020-02-02T00:00:00Z'
        try:
            validate_expiration_date(candidate)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
