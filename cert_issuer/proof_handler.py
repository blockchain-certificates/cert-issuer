from cert_issuer.chained_proof_2021 import ChainedProof2021
from cert_schema import ContextUrls
from cert_issuer.utils import array_intersect

class ProofHandler:
    def add_proof (self, certificate_json, merkle_proof):
        if 'proof' in certificate_json:
            if not isinstance(certificate_json['proof'], list):
                # convert proof to list
                initial_proof = certificate_json['proof']
                certificate_json['proof'] = [initial_proof]
            previous_proof = certificate_json['proof'][-1]
            certificate_json['proof'].append(ChainedProof2021(previous_proof, merkle_proof).to_json_object())
            self.update_context_for_chained_proof(certificate_json)
        else:
            certificate_json['proof'] = merkle_proof
        return certificate_json

    def update_context_for_chained_proof (self, certificate_json):
        context = certificate_json['@context']
        contextUrlsInstance = ContextUrls()
        if contextUrlsInstance.merkle_proof_2019() not in context:
            context.append(contextUrlsInstance.merkle_proof_2019())

        if contextUrlsInstance.chained_proof_2021() not in context:
            context.append(contextUrlsInstance.chained_proof_2021())

        if array_intersect(contextUrlsInstance.v3_all(), context):
            for v3_context in contextUrlsInstance.v3_all():
                if v3_context in context:
                    index = context.index(v3_context)
                    del context[index]
            context.append(contextUrlsInstance.v3_1_canonical())
