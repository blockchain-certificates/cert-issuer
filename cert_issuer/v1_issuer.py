import sys

import hashlib

from cert_issuer import trx_utils
from cert_issuer.helpers import hexlify
from cert_issuer.issuer import Issuer
from cert_issuer.models import TransactionData
from cert_issuer.models import convert_file_name

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


class V1Issuer(Issuer):
    def __init__(self, config, certificates_to_issue):
        Issuer.__init__(self, config, certificates_to_issue)

    def do_hash_certificate(self, certificate):
        return hashlib.sha256(certificate).hexdigest()

    def get_cost_for_certificate_batch(self, dust_threshold, recommended_fee_per_transaction, satoshi_per_byte,
                                       allow_transfer):
        num_certificates = len(self.certificates_to_issue)
        num_outputs = Issuer.get_num_outputs(num_certificates)
        return Issuer.get_cost_for_certificate_batch(dust_threshold, recommended_fee_per_transaction,
                                                     satoshi_per_byte, num_outputs, allow_transfer, num_certificates,
                                                     num_certificates)

    def create_transactions(self, wallet, revocation_address, issuing_transaction_cost,
                            split_input_trxs):

        unspent_outputs = wallet.get_unspent_outputs(self.issuing_address)
        current_tail = -1

        txs = []
        for uid, certificate_metadata in self.certificates_to_issue.items():
            last_output = unspent_outputs[current_tail]

            with open(certificate_metadata.certificate_hash_file_name, 'rb') as in_file:
                op_return_value = in_file.read()

            # send a transaction to the recipient's public key, and to a
            # revocation address
            txouts = trx_utils.create_recipient_outputs(certificate_metadata.pubkey, revocation_address,
                                                        issuing_transaction_cost.min_per_output)

            tx = trx_utils.create_trx(op_return_value, issuing_transaction_cost, self.issuing_address, txouts,
                                      last_output)

            unsigned_tx_file_name = convert_file_name(
                self.config.unsigned_txs_file_pattern, uid)
            unsent_tx_file_name = convert_file_name(
                self.config.signed_txs_file_pattern, uid)
            sent_tx_file_name = convert_file_name(
                self.config.sent_txs_file_pattern, uid)
            td = TransactionData(uid=certificate_metadata.uid,
                                 tx=tx,
                                 tx_input=last_output,
                                 op_return_value=hexlify(op_return_value),
                                 unsigned_tx_file_name=unsigned_tx_file_name,
                                 signed_tx_file_name=unsent_tx_file_name,
                                 sent_tx_file_name=sent_tx_file_name)
            txs.append(td)
            if split_input_trxs:
                current_tail -= 1
        return txs
