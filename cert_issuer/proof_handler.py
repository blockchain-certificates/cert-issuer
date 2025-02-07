from cert_issuer.proof_suites.merkle_proof_2019 import MerkleProof2019Suite
from cert_schema import ContextUrls
from cert_issuer.utils import array_intersect

class ProofHandler:
    def __init__(self):
        self.contextUrls = ContextUrls()

    def add_proof(self, certificate_json, merkle_proof, app_config=None):
        if 'proof' in certificate_json:
            if not isinstance(certificate_json['proof'], list):
                # convert proof to list
                initial_proof = certificate_json['proof']
                certificate_json['proof'] = [initial_proof]
            if self.is_multiple_proof_config_chained(app_config):
                self.add_chained_proof(certificate_json, merkle_proof)
            else:
                certificate_json['proof'].append(merkle_proof)
        else:
            certificate_json['proof'] = merkle_proof
        self.update_context_for_proof(certificate_json)
        return certificate_json

    def add_merkle_proof_2019(self, certificate_json, proof_value, app_config):
        merkle_proof = MerkleProof2019Suite(proof_value, app_config)
        certificate_json = self.add_proof(certificate_json, merkle_proof.to_json_object(), app_config)
        return certificate_json

    def is_multiple_proof_config_chained(self, app_config):
        if app_config is None:
            return True
        return app_config.multiple_proofs == 'chained'

    def add_chained_proof(self, certificate_json, merkle_proof):
        previous_proof = certificate_json['proof'][-1]
        merkle_proof['previousProof'] = previous_proof['id']
        certificate_json['proof'].append(merkle_proof)

    def update_context_for_proof(self, certificate_json):
        context = certificate_json['@context']

        if self.contextUrls.data_integrity_proof_v2() not in context:
            context.append(self.contextUrls.data_integrity_proof_v2())

        if array_intersect(self.contextUrls.v3_all(), context):
            for v3_context in self.contextUrls.v3_all():
                if v3_context in context:
                    index = context.index(v3_context)
                    del context[index]
            context.append(self.contextUrls.v3_1_canonical())
