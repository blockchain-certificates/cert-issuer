from collections import namedtuple

CertificateMetadata = namedtuple(
    'CertificateMetadata', ['uid', 'public_key', 'revocation_key', 'unsigned_certificate_file_name',
                            'signed_certificate_file_name', 'certificate_hash_file_name'])

TransactionData = namedtuple(
    'TransactionData', ['uid', 'tx', 'tx_input', 'op_return_value', 'unsigned_tx_file_name', 'signed_tx_file_name',
                        'sent_tx_file_name'])


def make_certificate_metadata(config, uid, public_key, revocation_key=None):
    unsigned_certificate_file_name = convert_file_name(config.unsigned_certs_file_pattern, uid)
    signed_certificate_file_name = convert_file_name(config.signed_certs_file_pattern, uid)
    certificate_hash_file_name = convert_file_name(config.hashed_certs_file_pattern, uid)

    return CertificateMetadata(uid=uid, public_key=public_key, revocation_key=revocation_key,
                               unsigned_certificate_file_name=unsigned_certificate_file_name,
                               signed_certificate_file_name=signed_certificate_file_name,
                               certificate_hash_file_name=certificate_hash_file_name)


def convert_file_name(to_pattern, cert_uid):
    return to_pattern.replace('*', cert_uid)


class TransactionCosts:
    """
    Represents costs for an issuing event, including the issuing transaction and transfer costs if applicable
    """

    def __init__(self, min_per_output, fee, total):
        self.min_per_output = min_per_output
        self.fee = fee
        self.total = total
        self.transfer_cost = 0

    def set_transfer_fee(self, transfer_cost):
        self.transfer_cost = transfer_cost
        self.total += self.transfer_cost

    def difference(self, balance):
        if self.total <= balance:
            return 0
        return self.total - balance
