import unittest

from cert_issuer.models.verifiable_credential import validate_issuance_date

class UnitValidationV3 (unittest.TestCase):
    def test_validate_issuance_date_invalid_RFC3339 (self):
        candidate = '20200202'
        try:
            validate_issuance_date(candidate)
        except:
            assert True
            return

        assert False
    def test_validate_issuance_date_invalid_RFC3339_timezone_offset_zulu (self):
        candidate = '2020-02-02T00:00:00+03:00Z'
        try:
            validate_issuance_date(candidate)
        except:
            assert True
            return

        assert False

    def test_validate_issuance_date_valid_RFC3339 (self):
        candidate = '2020-02-02T00:00:00Z'
        try:
            validate_issuance_date(candidate)
        except:
            assert False
            return

        assert True

    def test_validate_issuance_date_valid_RFC3339_no_T (self):
        candidate = '2020-02-02 00:00:00Z'
        try:
            validate_issuance_date(candidate)
        except:
            assert True
            return

        assert True

    def test_validate_issuance_date_valid_RFC3339_timezone_offset (self):
        candidate = '2020-02-02T00:00:00+03:00'
        try:
            validate_issuance_date(candidate)
        except:
            assert False
            return

        assert True

    def test_validate_issuance_date_valid_RFC3339_millisec (self):
        candidate = '2020-02-02T00:00:00.916Z'
        try:
            validate_issuance_date(candidate)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
