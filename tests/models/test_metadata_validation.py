import json
import logging
import unittest
from cert_issuer.models.metadata import validate_metadata_structure
from kgb import SpyAgency

class MetadataValidationTestSuite(unittest.TestCase):
    def test_json_schema_validation_is_valid(self):
        metadata_string = "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{},\"displayOrder\":[\"certificate.issuingInstitution\"]}"
        try:
            validate_metadata_structure(json.loads(metadata_string))
        except Exception as e:
            print(e)
            assert False
            return

        assert True

    def test_json_schema_validation_is_invalid(self):
        metadata_string = "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{},\"displayOrder\":{\"certificate.issuingInstitution\":1}}"
        try:
            validate_metadata_structure(json.loads(metadata_string))
        except Exception as e:
            assert True
            return

        assert False

    def test_json_schema_validation_no_schema(self):
        spy = SpyAgency()
        spy.spy_on(logging.warning)
        metadata_string = "{\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{},\"displayOrder\":[\"certificate.issuingInstitution\"]}"
        try:
            validate_metadata_structure(json.loads(metadata_string))
        except Exception as e:
            print(e)
            logging.warning.unspy()
            assert False
            return

        self.assertTrue(
            logging.warning.calls[0].called_with("""
            The metadata object provided with the certificate does not include a `schema` property.
            Not defining such property will result in errors in the rendering of the metadata property in the UI projects. 
            """)
        )
        logging.warning.unspy()

    def test_json_schema_validation_no_display_order(self):
        spy = SpyAgency()
        spy.spy_on(logging.warning)
        metadata_string = "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{}}"
        try:
            validate_metadata_structure(json.loads(metadata_string))
        except Exception as e:
            print(e)
            logging.warning.unspy()
            assert False
            return

        self.assertTrue(
            logging.warning.calls[0].called_with("""
           The metadata object provided with the certificate does not include a `displayOrder` property.
           Not defining such property will result in errors in the rendering of the metadata property in the UI projects. 
           """)
        )
        logging.warning.unspy()

    def test_json_schema_validation_display_order(self):
        spy = SpyAgency()
        spy.spy_on(logging.warning)
        metadata_string = "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{},\"displayOrder\":[\"certificate.issuingInstitution\", \"recipient.name\", \"class.year\", \"class.professor\", \"recipient.email\"]}"
        try:
            validate_metadata_structure(json.loads(metadata_string))
        except Exception as e:
            print(e)
            logging.warning.unspy()
            assert False
            return

        self.assertTrue(
            logging.warning.calls[0].called_with(
                '`metadata.displayOrder` property references a property named: \x1b[1m%s\x1b[0m which does not exist in group: \x1b[1m%s\x1b[0m.',
                'name',
                'recipient'
            )
        )
        self.assertTrue(
            logging.warning.calls[1].called_with(
                '`metadata.displayOrder` property references a group named: \x1b[1m%s\x1b[0m which does not exist in metadata object.',
                'class'
            )
        )
        self.assertTrue(
            logging.warning.calls[2].called_with(
                '`metadata.displayOrder` property references a property named: \x1b[1m%s\x1b[0m which does not exist in group: \x1b[1m%s\x1b[0m.',
                'email',
                'recipient'
            )
        )
        logging.warning.unspy()

    def test_json_schema_validation_property_title(self):
        spy = SpyAgency()
        spy.spy_on(logging.warning)
        metadata_string = "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"dean\":{\"type\":\"string\"},\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\",\"dean\":\"John Rambo\"},\"recipient\":{},\"displayOrder\":[\"certificate.issuingInstitution\", \"certificate.dean\"]}"
        try:
            validate_metadata_structure(json.loads(metadata_string))
        except Exception as e:
            print(e)
            logging.warning.unspy()
            assert False
            return

        print(logging.warning.calls[0].args)
        self.assertTrue(
            logging.warning.calls[0].called_with(
                """No title has been defined for property: \x1b[1mdean\x1b[0m in group: \x1b[1mcertificate\x1b[0m.\n            Title should be defined under path `schema.properties.certificate.properties.dean.title`"""
            )
        )
        logging.warning.unspy()
