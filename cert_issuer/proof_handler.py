from cert_issuer.chained_proof_2021 import ChainedProof2021

class ProofHandler:
    def add_proof (self, certificate_json, merkle_proof):
        if 'proof' in certificate_json:
            if not isinstance(certificate_json['proof'], list):
                # convert proof to list
                initial_proof = certificate_json['proof']
                certificate_json['proof'] = [initial_proof]
            previous_proof = certificate_json['proof'][-1]
            certificate_json['proof'].append(ChainedProof2021(previous_proof, merkle_proof).to_json_object())
        else:
            certificate_json['proof'] = merkle_proof
        return certificate_json
