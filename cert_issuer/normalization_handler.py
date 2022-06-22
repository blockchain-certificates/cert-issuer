import json
import os
from cert_schema import normalize_jsonld, extend_preloaded_context

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class JSONLDHandler:
    @staticmethod
    def normalize_to_utf8(certificate_json):
        with open(os.path.join(BASE_DIR, '../data/context/ed25519.v1.json')) as context_file:
            context_data = json.load(context_file)
            extend_preloaded_context('https://w3id.org/security/suites/ed25519-2020/v1', context_data)
        normalized = normalize_jsonld(certificate_json, detect_unmapped_fields=False)
        return normalized.encode('utf-8')
