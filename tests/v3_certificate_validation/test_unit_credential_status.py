import unittest

from cert_issuer.models.verifiable_credential import validate_credential_status

class UnitValidationV3 (unittest.TestCase):
    def test_validate_credential_status_undefined_id (self):
        candidate = {
            "type": 'a type'
        }
        try:
            validate_credential_status(candidate)
        except:
            assert True
            return
    def test_validate_credential_status_invalid_id (self):
        candidate = {
            "id": 'not a url',
            "type": 'a type'
        }
        try:
            validate_credential_status(candidate)
        except:
            assert True
            return

        assert False

    def test_validate_credential_status_undefined_type (self):
        candidate = {
            "id": 'https://valid.path'
        }
        try:
            validate_credential_status(candidate)
        except:
            assert True
            return

        assert False

    def test_validate_credential_status_valid (self):
        candidate = {
            "id": 'https://valid.path',
            "type": 'statusList'
        }
        try:
            validate_credential_status(candidate)
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
