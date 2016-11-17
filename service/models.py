from enum import Enum

class IssuingState(Enum):
    downloading_unsigned_certs = 1
    signing_certs = 2
    issuing_certs = 3
    uploading_results = 4
    succeeded = 5
    failed = 6


# , issuer_key, revocation_key
class IssuingRequest(object):
    def __init__(self, batch_id, s3_base, chain):
        self.batch_id = batch_id
        self.s3_base = s3_base
        self.chain = chain
        self.state = IssuingState.downloading_unsigned_certs

