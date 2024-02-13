from datetime import datetime

MERKLE_PROOF_2019_TYPE = 'MerkleProof2019'
class MerkleProof2019Suite:
    type = ''
    verificationMethod = ''
    created = ''
    proofPurpose = ''
    previousProof = ''
    proofValue = ''

    def __init__(self, proof_value, verificationMethod):
        self.type = MERKLE_PROOF_2019_TYPE
        self.proofPurpose = 'assertionMethod'
        self.created = self.get_creation_time()
        self.proofValue = proof_value.decode('utf-8')
        self.verificationMethod = verificationMethod

    def get_creation_time(self):
        return datetime.now().isoformat()

    def to_json_object(self):
        return self.__dict__
