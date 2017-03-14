import hashlib
import json
from abc import abstractmethod

from cert_schema import jsonld_document_loader
from cert_schema import validate_unsigned_v1_2
from cert_schema import validate_v2
from pyld import jsonld
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()


def cached_document_loader(url, override_cache=False):
    if not override_cache:
        result = cache.get(url)
        if result:
            return result
    doc = jsonld_document_loader(url)
    cache.set(url, doc)
    return doc


def normalize_jsonld(certificate_json):
    """
    Normalize the JSON-LD certificate
    :param certificate_json:
    :return:
    """
    options = {'algorithm': 'URDNA2015', 'format': 'application/nquads', 'documentLoader': cached_document_loader}
    normalized = jsonld.normalize(certificate_json, options=options)
    return normalized


def hash_normalized_jsonld(normalized):
    """
    Hash the JSON-LD normalized certificate
    :param certificate:
    :return:
    """
    hashed = hashlib.sha256(bytes(normalized, 'utf-8')).hexdigest()
    return hashed


class CertificateHandler(object):
    def __init__(self, certificates_to_issue):
        self.certificates_to_issue = certificates_to_issue

    @abstractmethod
    def validate(self, certificate_json):
        pass

    @abstractmethod
    def get_message_to_sign(self, certificate_json):
        pass

    @abstractmethod
    def combine_signature_with_certificate(self, certificate_json, signature):
        pass

    @abstractmethod
    def create_receipt(self, uid, merkle_proof, certificate_json):
        pass

    @abstractmethod
    def get_certificate_to_issue(self, uid):
        pass


class CertificateV1_2Handler(CertificateHandler):
    def __init__(self, certificates_to_issue):
        super().__init__(certificates_to_issue)

    def validate(self, certificate_json):
        validate_unsigned_v1_2(certificate_json)

    def get_message_to_sign(self, certificate_json):
        to_sign = certificate_json['assertion']['uid']
        return to_sign

    def combine_signature_with_certificate(self, certificate_json, signature):
        certificate_json['signature'] = signature
        sorted_cert = json.dumps(certificate_json, sort_keys=True)
        return sorted_cert

    def create_receipt(self, uid, merkle_proof, certificate_json):
        """
        :param uid:
        :param merkle_proof:
        :param certificate_json:
        :return:
        """
        blockchain_cert = {
            '@context': 'https://w3id.org/blockcerts/v1',
            'type': 'BlockchainCertificate',
            'document': certificate_json,
            'receipt': merkle_proof
        }
        return blockchain_cert

    def get_certificate_to_issue(self, uid):
        metadata = self.certificates_to_issue[uid]
        with open(metadata.signed_cert_file_name) as cert:
            cert_json = json.load(cert)
            return cert_json


class CertificateV2Handler(CertificateHandler):
    def __init__(self, certificates_to_issue):
        super().__init__(certificates_to_issue)

    def validate(self, certificate_json):
        validate_v2(certificate_json)

    def get_message_to_sign(self, certificate_json):
        normalized = normalize_jsonld(certificate_json)
        return normalized

    def combine_signature_with_certificate(self, certificate_json, signature):
        return signature

    def create_receipt(self, uid, merkle_proof, certificate_json):
        cert_metadata = self.certificates_to_issue[uid]
        with open(cert_metadata.signed_cert_file_name) as signature_file:
            cert_signature = signature_file.read()
        signature = {
            "@context": "http://www.blockcerts.org/blockcerts_v2_alpha/context_bc.json",
            "type": [
                "EcdsaKoblitzSignature2016",
                "Extension"
            ],
            "merkleProof": merkle_proof,
            "creator": "https://example.org/issuer/keys/1.9.1.1",
            "created": "2016-09-23T20:21:34Z",
            "signatureValue": cert_signature
        }

        certificate_json['bc_ext:signature'] = signature
        return certificate_json

    def get_certificate_to_issue(self, uid):
        metadata = self.certificates_to_issue[uid]
        with open(metadata.unsigned_cert_file_name) as cert:
            cert_json = json.load(cert)
            return cert_json
