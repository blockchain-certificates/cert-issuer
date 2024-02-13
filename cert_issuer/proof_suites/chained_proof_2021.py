import copy
CHAINED_PROOF_TYPE = 'ChainedProof2021'

class ChainedProof2021:
    type = ''
    verificationMethod = ''
    chainedProofType = ''
    created = ''
    proofPurpose = ''
    previousProof = ''
    proofValue = ''

    def __init__(self, previous_proof, current_proof):
        self.type = CHAINED_PROOF_TYPE
        self.create_proof_object(current_proof)
        self.set_previous_proof(previous_proof)

    def create_proof_object(self, current_proof):
        self.verificationMethod = current_proof['verificationMethod']
        self.chainedProofType = current_proof['type']
        self.created = current_proof['created']
        self.proofPurpose = current_proof['proofPurpose']
        self.proofValue = current_proof['proofValue']

    def set_previous_proof(self, previous_proof):
        if previous_proof['type'] == CHAINED_PROOF_TYPE:
            previous_proof_to_store = copy.deepcopy(previous_proof)
            previous_proof_to_store['type'] = previous_proof['chainedProofType']
            del previous_proof_to_store['chainedProofType']
            del previous_proof_to_store['previousProof']
            self.previousProof = previous_proof_to_store
        else:
            self.previousProof = previous_proof

    def to_json_object(self):
        return self.__dict__
