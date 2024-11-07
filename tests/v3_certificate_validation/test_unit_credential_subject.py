import unittest

from cert_issuer.models.verifiable_credential import validate_credential_subject

class UnitValidationV3 (unittest.TestCase):
    def test_null (self):
        credential_subject = None

        # TODO: ideally this would be stubbed to have better control over the test
        # TODO: however urlretrieve and consumption is a bit convoluted to mock
        credential_schema = {
            "id": "https://www.blockcerts.org/samples/3.0/example-id-card-schema.json",
            "type": "JsonSchema"
        }

        try:
            validate_credential_subject(credential_subject, credential_schema)
        except:
            assert True
            return

        assert False

    def test_conforms_to_schema (self):
        credential_subject = {
            "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
            "name": "John Smith",
            "nationality": "Canada",
            "DOB": "05/10/1983",
            "height": "1.80m",
            "residentialAddressStreet": "6 Maple Tree street",
            "residentialAddressTown": "Toronto",
            "residentialAddressPostCode": "YYZYUL"
        }

        # TODO: ideally this would be stubbed to have better control over the test
        # TODO: however urlretrieve and consumption is a bit convoluted to mock
        credential_schema = {
            "id": "https://www.blockcerts.org/samples/3.0/example-id-card-schema.json",
            "type": "JsonSchema"
        }

        try:
            validate_credential_subject(credential_subject, credential_schema)
        except:
            assert False
            return

        assert True

    def test_array_conforms_to_schema (self):
        credential_subject = [
            {
              "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
              "language": "en",
              "name": "John Smith",
              "nationality": "Canada",
              "DOB": "05/10/1983",
              "height": "1.80m",
              "residentialAddressStreet": "6 Maple Tree street",
              "residentialAddressTown": "Toronto",
              "residentialAddressPostCode": "YYZYUL"
            },
            {
              "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
              "language": "fr",
              "name": "Jean Forgeron",
              "nationality": "Canada",
              "DOB": "05/10/1983",
              "height": "1.80m",
              "residentialAddressStreet": "6 rue des Érables",
              "residentialAddressTown": "Montréal",
              "residentialAddressPostCode": "YYZYUL"
            }
        ]

        # TODO: ideally this would be stubbed to have better control over the test
        # TODO: however urlretrieve and consumption is a bit convoluted to mock
        credential_schema = {
            "id": "https://www.blockcerts.org/samples/3.0/example-id-card-schema.json",
            "type": "JsonSchema"
        }

        try:
            validate_credential_subject(credential_subject, credential_schema)
        except:
            assert False
            return

        assert True

    def test_array_does_not_conform_to_schema (self):
        credential_subject = [
            {
              "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
              "language": "en",
              "name": "John Smith",
              "nationality": "Canada",
              "DOB": "05/10/1983",
              "height": "1.80m",
              "residentialAddressStreet": "6 Maple Tree street",
              "residentialAddressTown": "Toronto",
              "residentialAddressPostCode": "YYZYUL"
            },
            {
              "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
              "language": "fr",
              "name": "Jean Forgeron",
              "DOB": "05/10/1983",
              "height": "1.80m",
              "residentialAddressStreet": "6 rue des Érables",
              "residentialAddressTown": "Montréal",
              "residentialAddressPostCode": "YYZYUL"
            }
        ]

        # TODO: ideally this would be stubbed to have better control over the test
        # TODO: however urlretrieve and consumption is a bit convoluted to mock
        credential_schema = {
            "id": "https://www.blockcerts.org/samples/3.0/example-id-card-schema.json",
            "type": "JsonSchema"
        }

        try:
            validate_credential_subject(credential_subject, credential_schema)
        except:
            assert True
            return

        assert False

    def test_does_not_conform_to_schema (self):
        credential_subject = {
            "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
            "name": "John Smith",
            "DOB": "05/10/1983",
            "height": "1.80m",
            "residentialAddressStreet": "6 Maple Tree street",
            "residentialAddressTown": "Toronto",
            "residentialAddressPostCode": "YYZYUL"
        }

        # TODO: ideally this would be stubbed to have better control over the test
        # TODO: however urlretrieve and consumption is a bit convoluted to mock
        credential_schema = {
            "id": "https://www.blockcerts.org/samples/3.0/example-id-card-schema.json",
            "type": "JsonSchema"
        }

        try:
            validate_credential_subject(credential_subject, credential_schema)
        except:
            assert True
            return

        assert False
