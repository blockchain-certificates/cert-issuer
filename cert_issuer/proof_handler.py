from cert_issuer.chained_proof_2021 import ChainedProof2021

class ProofHandler:
    def add_proof (self, certificate_json, merkle_proof):
        if 'proof' in certificate_json:
            initial_proof = certificate_json['proof']
            certificate_json['proof'] = [initial_proof, ChainedProof2021(initial_proof, merkle_proof).toJsonObject()]
        else:
            certificate_json['proof'] = merkle_proof
        return certificate_json
