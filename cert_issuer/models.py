from collections import namedtuple

TransactionOutput = namedtuple(
    'TxOutput', ['outpoint', 'address', 'script_pub_key', 'amount'])

TransactionData = namedtuple(
    'TransactionData', ['uid', 'tx', 'tx_input', 'op_return_value', 'unsigned_tx_file_name', 'signed_tx_file_name',
                        'sent_tx_file_name'])


def convert_file_name(to_pattern, cert_uid):
    return to_pattern.replace('*', cert_uid)


class CertificateMetadata:
    def __init__(self, config, uid, pubkey):
        self.uid = uid
        self.pubkey = pubkey
        self.signed_certificate_file_name = convert_file_name(
            config.signed_certs_file_pattern, uid)
        self.certificate_hash_file_name = convert_file_name(
            config.hashed_certs_file_pattern, uid)
        self.unsigned_tx_file_name = convert_file_name(
            config.unsigned_txs_file_pattern, uid)
        self.unsent_tx_file_name = convert_file_name(
            config.unsent_txs_file_pattern, uid)
        self.sent_tx_file_name = convert_file_name(
            config.sent_txs_file_pattern, uid)
        self.proof_file_name = convert_file_name(
            config.proof_file_pattern, uid)


class AllCosts:
    def __init__(self, number_of_transactions, issuing_transaction_cost, transfer_cost):
        self.number_of_transactions = number_of_transactions
        self.issuing_transaction_cost = issuing_transaction_cost
        self.transfer_cost = transfer_cost
        self.total = number_of_transactions * issuing_transaction_cost.total + transfer_cost.total

    def difference(self, balance):
        if self.total <= balance:
            return 0
        return self.total - balance


class TransactionCosts:
    """
    Represents transaction costs
    """

    def __init__(self, min_per_output, fee, total):
        self.min_per_output = min_per_output
        self.fee = fee
        self.total = total

    def difference(self, balance):
        if self.total <= balance:
            return 0
        return self.total - balance
