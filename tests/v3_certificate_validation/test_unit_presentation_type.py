import unittest

from cert_issuer.models import validate_type

class UnitValidationV3 (unittest.TestCase):
    def test_validate_type_valid_presentation_type (self):
        valid_type = ['VerifiablePresentation']
        try:
            validate_type(valid_type)
        except:
            assert False
            return

        assert True

    def test_validate_type_invalid_presentation_type (self):
        valid_type = ['SomethingSomething']
        try:
            validate_type(valid_type)
        except:
            assert True
            return

        assert False

    def test_validate_type_invalid_presentation_shape (self):
        valid_type = 'VerifiablePresentation'
        try:
            validate_type(valid_type)
        except:
            assert True
            return

        assert False

    def test_validate_type_invalid_presentation_definition (self):
        valid_type = []
        try:
            validate_type(valid_type)
        except:
            assert True
            return

        assert False

if __name__ == '__main__':
    unittest.main()
