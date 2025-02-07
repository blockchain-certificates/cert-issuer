import uuid
from datetime import datetime, timezone, tzinfo

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

    def __init__(self, proof_value, app_config):
        verification_method = app_config.verification_method
        issuance_timezone = app_config.issuance_timezone or 'UTC'
        self.id = 'urn:uuid:' + str(uuid.uuid4())
        self.type = DATA_INTEGRITY_PROOF_TYPE
        self.cryptosuite = MERKLE_PROOF_2019_TYPE
        self.proofPurpose = 'assertionMethod'
        self.created = self.get_creation_time(issuance_timezone)
        self.proofValue = proof_value.decode('utf-8')
        self.verificationMethod = verification_method

    def get_creation_time(self, issuance_timezone):
        if issuance_timezone == 'UTC':
            return datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + 'Z'
        else:
            return datetime.now().astimezone().replace(microsecond=0).isoformat()

    def to_json_object(self):
        return self.__dict__
