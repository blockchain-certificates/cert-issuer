import datetime
import hashlib
import json
from abc import abstractmethod

import pytz
from cert_core import PUBKEY_PREFIX
from cert_core import parse_chain_from_address
from cert_schema import validate_unsigned_v1_2
from cert_schema import validate_v2
from ld_koblitz_signatures import signatures
from ld_koblitz_signatures.document_loader import jsonld_document_loader
from ld_koblitz_signatures.signatures import SignatureOptions
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


def hash_normalized_jsonld(normalized):
    """
    Hash the JSON-LD normalized certificate
    :param certificate:
    :return:
    """
    hashed = hashlib.sha256(bytes(normalized, 'utf-8')).hexdigest()
    return hashed


class CertificateBatchHandler(object):
    """
    Manages a batch of certificates. Responsible for iterating certificates in a consistent order.

    In this case, certificates are initialized as an Ordered Dictionary, and we iterate in insertion order.
    """
    def __init__(self, certificates_to_issue, certificate_handler):
        self.certificates_to_issue = certificates_to_issue
        self.certificate_handler = certificate_handler

    def validate_batch(self):
        """
        Propagates exception on failure
        :return:
        """
        for _, metadata in self.certificates_to_issue.items():
            self.certificate_handler.validate_certificate(metadata)

    def sign_batch(self, signer):
        for _, metadata in self.certificates_to_issue.items():
            self.certificate_handler.sign_certificate(signer, metadata)

    def create_node_generator(self):
        for uid, metadata in self.certificates_to_issue.items():
            cert_json = self.certificate_handler.get_certificate_to_issue(metadata)
            normalized = signatures.normalize_jsonld(cert_json)
            hashed = hash_normalized_jsonld(normalized)
            yield hashed

    def add_proofs(self, generator, tree):
        gen = generator(tree)
        for uid, metadata in self.certificates_to_issue.items():
            merkle_proof = next(gen)
            self.certificate_handler.add_proof(metadata, merkle_proof)


class CertificateHandler(object):
    @abstractmethod
    def validate_certificate(self, certificate_metadata):
        pass

    @abstractmethod
    def sign_certificate(self, signer, certificate_metadata):
        pass

    @abstractmethod
    def get_certificate_to_issue(self, certificate_metadata):
        pass

    @abstractmethod
    def add_proof(self, certificate_metadata, merkle_proof):
        pass


class CertificateV1_2Handler(CertificateHandler):
    def validate_certificate(self, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name) as cert:
            certificate_json = json.load(cert)
            validate_unsigned_v1_2(certificate_json)

    def sign_certificate(self, signer, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name, 'r') as cert, \
                open(certificate_metadata.signed_cert_file_name, 'w') as signed_cert_file:
            certificate_json = json.load(cert)
            to_sign = certificate_metadata.uid
            signature = signer.sign_message(to_sign)
            certificate_json['signature'] = signature
            sorted_cert = json.dumps(certificate_json, sort_keys=True)
            signed_cert_file.write(sorted_cert)

    def get_certificate_to_issue(self, certificate_metadata):
        with open(certificate_metadata.signed_cert_file_name, 'r') as signed_cert_file:
            certificate_json = json.load(signed_cert_file)
        return certificate_json

    def add_proof(self, certificate_metadata, merkle_proof):
        """
        :param certificate_metadata:
        :param merkle_proof:
        :return:
        """
        certificate_json = self.get_certificate_to_issue(certificate_metadata)
        blockchain_certificate = {
            '@context': 'https://w3id.org/blockcerts/v1',
            'type': 'BlockchainCertificate',
            'document': certificate_json,
            'receipt': merkle_proof
        }
        with open(certificate_metadata.blockchain_cert_file_name, 'w') as out_file:
            out_file.write(json.dumps(blockchain_certificate))


class CertificateV2Handler(CertificateHandler):
    def validate_certificate(self, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name) as cert:
            certificate_json = json.load(cert)
            validate_v2(certificate_json)

    def sign_certificate(self, signer, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name, 'r') as cert, \
                open(certificate_metadata.signed_cert_file_name, 'w') as signed_cert_file:
            certificate_json = json.load(cert)

            iso_datetime_pre = datetime.datetime.now(pytz.timezone('GMT')).replace(microsecond=0).isoformat()
            iso_datetime = str(iso_datetime_pre).replace('+00:00', 'Z')
            creator_address = PUBKEY_PREFIX + signer.issuing_address

            options = SignatureOptions(iso_datetime, creator_address)
            signed = signatures.sign(certificate_json, signer.wif, options,
                            parse_chain_from_address(signer.issuing_address).name)
            signed['signature']['type'] = ['EcdsaKoblitzSignature2016', 'Extension', 'LinkedDataEcdsaKoblitzSignature']

            signed_cert_file.write(json.dumps(signed))

    def get_certificate_to_issue(self, certificate_metadata):
        with open(certificate_metadata.unsigned_cert_file_name, 'r') as unsigned_cert_file:
            certificate_json = json.load(unsigned_cert_file)
        return certificate_json

    def add_proof(self, certificate_metadata, merkle_proof):
        """
        :param certificate_metadata:
        :param merkle_proof:
        :return:
        """
        certificate_json = self.get_certificate_to_issue(certificate_metadata)
        with open(certificate_metadata.signed_cert_file_name) as signature_file:
            cert_signature = json.load(signature_file)

        cert_signature['signature']['merkleProof'] = merkle_proof

        with open(certificate_metadata.blockchain_cert_file_name, 'w') as out_file:
            out_file.write(json.dumps(cert_signature))
