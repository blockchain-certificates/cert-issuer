import unittest

from cert_issuer.models.verifiable_credential import validate_prop_type_and_id

class UnitValidationV3 (unittest.TestCase):
    def test_validate_credential_status_undefined_id (self):
        candidate = {
            "type": 'a type'
        }
        try:
            validate_prop_type_and_id(candidate, 'credentialStatus')
        except:
            assert True
            return
    def test_validate_credential_status_invalid_id (self):
        candidate = {
            "id": 'not a url',
            "type": 'a type'
        }
        try:
            validate_prop_type_and_id(candidate, 'credentialStatus')
        except:
            assert True
            return

        assert False

    def test_validate_credential_status_undefined_type (self):
        candidate = {
            "id": 'https://valid.path'
        }
        try:
            validate_prop_type_and_id(candidate, 'credentialStatus')
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
            validate_prop_type_and_id(candidate, 'credentialStatus')
        except:
            assert False
            return

        assert True

if __name__ == '__main__':
    unittest.main()
