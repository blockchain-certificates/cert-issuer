import uuid
from datetime import datetime

DATA_INTEGRITY_PROOF_TYPE = 'DataIntegrityProof'
MERKLE_PROOF_2019_TYPE = 'merkle-proof-2019'
class MerkleProof2019Suite:
    type = ''
    cryptosuite = ''
    verificationMethod = ''
    created = ''
    proofPurpose = ''
    previousProof = ''
    proofValue = ''

    def __init__(self, proof_value, verification_method, previous_proof = ''):
        self.id = 'urn:uuid:' + str(uuid.uuid4())
        self.type = DATA_INTEGRITY_PROOF_TYPE
        self.cryptosuite = MERKLE_PROOF_2019_TYPE
        self.proofPurpose = 'assertionMethod'
        self.created = self.get_creation_time()
        self.proofValue = proof_value.decode('utf-8')
        self.verificationMethod = verification_method
        if previous_proof != '':
            self.previousProof = previous_proof

    def get_creation_time(self):
        return datetime.now().isoformat()

    def to_json_object(self):
        return self.__dict__
