import unittest

from cert_issuer.models import validate_type

class UnitValidationV3 (unittest.TestCase):
    def test_validate_type_valid_credential_type (self):
        candidate = ['VerifiableCredential']
        try:
            validate_type(candidate)
        except:
            assert False
            return

        assert True

    def test_validate_type_invalid_credential_type (self):
        candidate = ['SomethingSomething']
        try:
            validate_type(candidate)
        except:
            assert True
            return

        assert False

    def test_validate_type_invalid_credential_shape (self):
        candidate = 'VerifiableCredential'
        try:
            validate_type(candidate)
        except:
            assert True
            return

        assert False

    def test_validate_type_invalid_credential_definition (self):
        candidate = []
        try:
            validate_type(candidate)
        except:
            assert True
            return

        assert False

if __name__ == '__main__':
    unittest.main()
