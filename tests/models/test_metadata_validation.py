import json
import unittest
from cert_issuer.models.metadata import validate_metadata_structure

class MetadataValidationTestSuite(unittest.TestCase):
    def test_json_schema_validation_is_valid(self):
        metadata_string = "{\"schema\":{\"$schema\":\"http://json-schema.org/draft-04/schema#\",\"type\":\"object\",\"properties\":{\"displayOrder\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}},\"certificate\":{\"order\":[],\"type\":\"object\",\"properties\":{\"issuingInstitution\":{\"title\":\"Issuing Institution\",\"type\":\"string\",\"default\":\"Learning Machine Technologies, Inc.\"}}},\"recipient\":{}}},\"certificate\":{\"issuingInstitution\":\"Learning Machine Technologies, Inc.\"},\"recipient\":{},\"displayOrder\":[\"certificate.issuingInstitution\"]}"
        try:
            validate_metadata_structure(json.loads(metadata_string))
        except:
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
