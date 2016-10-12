from collections import namedtuple

TransactionData = namedtuple(
    'TransactionData', ['uid', 'tx', 'tx_input', 'op_return_value', 'unsigned_tx_file_name', 'signed_tx_file_name',
                        'sent_tx_file_name'])


def convert_file_name(to_pattern, cert_uid):
    return to_pattern.replace('*', cert_uid)


class CertificateMetadata:
    def __init__(self, config, uid, public_key, revocation_key=None):
        self.uid = uid
        self.public_key = public_key
        self.revocation_key = revocation_key
        self.unsigned_certificate_file_name = convert_file_name(
            config.unsigned_certs_file_pattern, uid)
        self.signed_certificate_file_name = convert_file_name(
            config.signed_certs_file_pattern, uid)
        self.certificate_hash_file_name = convert_file_name(
            config.hashed_certs_file_pattern, uid)


class TotalCosts:
    """
    Represents total costs for an issuing event, including the issuing transaction and any transfer
    costs incurred.
    """

    def __init__(self, issuing_transaction_cost, transfer_cost):
        self.issuing_transaction_cost = issuing_transaction_cost
        self.transfer_cost = transfer_cost

        cost_to_issue = issuing_transaction_cost.total
        if transfer_cost:
            self.total = cost_to_issue + transfer_cost.total
        else:
            self.total = cost_to_issue

    def difference(self, balance):
        if self.total <= balance:
            return 0
        return self.total - balance


class TransactionCosts:
    """
    Represents cost of one transaction on the Bitcoin blockchain
    """

    def __init__(self, min_per_output, fee, total):
        self.min_per_output = min_per_output
        self.fee = fee
        self.total = total

    def difference(self, balance):
        if self.total <= balance:
            return 0
        return self.total - balance
