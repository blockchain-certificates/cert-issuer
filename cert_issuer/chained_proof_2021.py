import json

class ChainedProof2021:
    type = ''
    verificationMethod = ''
    chainedProofType = ''
    created = ''
    proofPurpose = ''
    previousProof = ''
    proofValue = ''

    def __init__ (self, previousProof, currentProof):
        self.type = 'ChainedProof2021'
        self.verificationMethod = currentProof['verificationMethod']
        self.chainedProofType = currentProof['type']
        self.created = currentProof['created']
        self.proofPurpose = currentProof['proofPurpose']
        self.previousProof = previousProof
        self.proofValue = currentProof['proofValue']

    def toJsonObject(self):
        return self.__dict__
