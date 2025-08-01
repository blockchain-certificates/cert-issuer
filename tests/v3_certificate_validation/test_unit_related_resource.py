import unittest

from cert_issuer.models.verifiable_credential import validate_related_resource

class UnitValidationV3 (unittest.TestCase):
    def test_single_valid_resource(self):
        valid = {
            'id': 'https://www.w3.org/ns/credentials/v2',
            'digestSRI': 'sha384-l/HrjlBCNWyAX91hr6LFV2Y3heB5Tcr6IeE4/Tje8YyzYBM8IhqjHWiWpr8+ZbYU',
            'digestMultibase': 'uEiBZlVztZpfWHgPyslVv6-UwirFoQoRvW1htfx963sknNA'
        }
        try:
            validate_related_resource(valid)
        except:
            assert False
            return


