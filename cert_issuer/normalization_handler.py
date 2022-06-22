from cert_schema import normalize_jsonld


class JSONLDHandler:
    @staticmethod
    def normalize_to_utf8(certificate_json):
        normalized = normalize_jsonld(certificate_json, detect_unmapped_fields=False)
        return normalized.encode('utf-8')
