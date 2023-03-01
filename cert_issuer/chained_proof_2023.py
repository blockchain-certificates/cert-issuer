import copy
from merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.normalization_handler import JSONLDHandler
from pycoin.serialize import b2h
CHAINED_PROOF_TYPE = 'ChainedProof2023'


class ChainedProof2023:
    type = ''
    verificationMethod = ''
    chainedProofType = ''
    created = ''
    proofPurpose = ''
    previousProof = ''
    proofValue = ''

    def __init__(self, previous_proofs, current_proof):
        self.type = CHAINED_PROOF_TYPE
        self.create_proof_object(current_proof)
        self.set_previous_proof(previous_proofs)

    def create_proof_object(self, current_proof):
        self.verificationMethod = current_proof['verificationMethod']
        self.chainedProofType = current_proof['type']
        self.created = current_proof['created']
        self.proofPurpose = current_proof['proofPurpose']
        self.proofValue = current_proof['proofValue']

    def set_previous_proof(self, previous_proofs):
        print("Setting Chained Proof 2023 previous proof merkle tree")
        merkle_generator = MerkleTreeGenerator()
        merkle_generator.populate(self.proof_generator(previous_proofs))
        merkle_root = merkle_generator.get_blockchain_data()
        print(merkle_generator.get_proofs())
        print(b2h(merkle_root))
        # if previous_proof['type'] == CHAINED_PROOF_TYPE:
        #     previous_proof_to_store = copy.deepcopy(previous_proof)
        #     previous_proof_to_store['type'] = previous_proof['chainedProofType']
        #     del previous_proof_to_store['chainedProofType']
        #     del previous_proof_to_store['previousProof']
        #     self.previousProof = previous_proof_to_store
        # else:
        #     self.previousProof = previous_proof

    def proof_generator(self, previous_proofs):
        for proof in previous_proofs:
            print(proof)
            # TODO: this is missing jsonld context for normalization, hash is wrong
            normalized_proof = JSONLDHandler.normalize_to_utf8(proof)
            print(normalized_proof)
            yield normalized_proof

    def to_json_object(self):
        return self.__dict__
