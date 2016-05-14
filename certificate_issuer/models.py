from collections import namedtuple

from certificate_issuer import helpers


TransactionOutput = namedtuple('TxOutput', ['outpoint', 'address', 'script_pub_key', 'amount'])


class CertificateMetadata:
    def __init__(self, config, uid, name, pubkey):
        self.uid = uid
        self.name = name
        self.pubkey = pubkey
        self.unsigned_certificate_file_name = helpers.convert_file_name(config.unsigned_certs_file_pattern, uid)
        self.signed_certificate_file_name = helpers.convert_file_name(config.signed_certs_file_pattern, uid)
        self.certificate_hash_file_name = helpers.convert_file_name(config.hashed_certs_file_pattern, uid)
        self.unsigned_tx_file_name = helpers.convert_file_name(config.unsigned_txs_file_pattern, uid)
        self.unsent_tx_file_name = helpers.convert_file_name(config.unsent_txs_file_pattern, uid)
        self.sent_tx_file_name = helpers.convert_file_name(config.sent_txs_file_pattern, uid)


class TransactionCosts:
    def __init__(self, cost_per_transaction, fee_per_transaction, number_of_transactions, transfer_split_fee=0):
        self.cost_per_transaction = cost_per_transaction
        self.fee_per_transaction = fee_per_transaction
        self.number_of_transactions = number_of_transactions
        self.transfer_split_fee = transfer_split_fee
        self.total = (cost_per_transaction * number_of_transactions) + transfer_split_fee

    def difference(self, balance):
        if self.total <= balance:
            return 0
        return self.total - balance
