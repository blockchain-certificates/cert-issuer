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
    def validate_certificate(self):
        pass

    @abstractmethod
    def sign_certificate(self):
        pass

    @abstractmethod
    def create_receipt(self, uid, merkle_proof, certificate_json):
        pass

    @abstractmethod
    def get_certificate_to_issue(self, uid):
        pass

    def validate_batch(self):
        """
        Propagates exception on failure
        :return:
        """
        for _, certificate in self.certificates_to_issue.items():
            with open(certificate.unsigned_cert_file_name) as cert:
                certificate_json = json.load(cert)
                self.validate_certificate(certificate_json)

    def sign_batch(self, signer):
        for _, certificate in self.certificates_to_issue.items():
            with open(certificate.unsigned_cert_file_name, 'r') as cert, \
                    open(certificate.signed_cert_file_name, 'w') as signed_cert_file:
                certificate_json = json.load(cert)
                result = self.sign_certificate(signer, certificate_json)
                signed_cert_file.write(result)

    def create_node_generator(self):
        for uid, certificate in self.certificates_to_issue.items():
            cert_json = self.get_certificate_to_issue(uid)
            normalized = normalize_jsonld(cert_json)
            hashed = hash_normalized_jsonld(normalized)
            yield hashed

    def add_proofs(self, generator, tree):
        gen = generator(tree)
        for uid, metadata in self.certificates_to_issue.items():
            merkle_proof = next(gen)
            certificate_json = self.get_certificate_to_issue(uid)
            blockchain_certificate = self.create_receipt(uid, merkle_proof, certificate_json)
            with open(metadata.blockchain_cert_file_name, 'w') as out_file:
                out_file.write(json.dumps(blockchain_certificate))


class CertificateV1_2Handler(CertificateHandler):
    def __init__(self, certificates_to_issue):
        super().__init__(certificates_to_issue)

    def validate_certificate(self, certificate_json):
        validate_unsigned_v1_2(certificate_json)

    def sign_certificate(self, signer, certificate_json):
        to_sign = certificate_json['assertion']['uid']
        signature = signer.sign_message(to_sign)
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

    def validate_certificate(self, certificate_json):
        validate_v2(certificate_json)

    def sign_certificate(self, signer, certificate_json):
        to_sign = normalize_jsonld(certificate_json)
        signature = signer.sign_message(to_sign)
        return signature
        return sorted_cert

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
