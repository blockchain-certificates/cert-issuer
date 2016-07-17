import sys

import random
from cert_issuer import cert_utils
from cert_issuer import trx_utils
from cert_issuer.helpers import unhexlify, hexlify
from cert_issuer.issuer import Issuer
from cert_issuer.models import TransactionData
from cert_issuer.models import convert_file_name

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)

unsigned_tx_file_name = 'unsigned_tx.txt'
signed_tx_file_name = 'signed_tx.txt'
sent_tx_file_name = 'sent_tx.txt'


class V2Issuer(Issuer):
    def __init__(self, config):
        Issuer.__init__(self, config)
        self.batch_id = '%024x' % random.randrange(16 ** 24)

    def get_cost_for_certificate_batch(self, dust_threshold, recommended_fee_per_transaction, satoshi_per_byte,
                                       num_certificates, allow_transfer):
        """
        Per certificate, we pay 2*min_per_output (which is based on dust) + fee. Note assumes 1 input
        per tx. We may also need to pay additional fees for splitting into temp addresses
        """
        num_outputs = Issuer.get_num_outputs(num_certificates)
        return Issuer.get_cost_for_certificate_batch(dust_threshold, recommended_fee_per_transaction, satoshi_per_byte,
                                                     num_outputs, allow_transfer, 1, 1)

    def create_transactions(self, wallet, revocation_address, certificates_to_issue, issuing_transaction_cost,
                            split_input_trxs):

        tree = cert_utils.build_merkle_tree(certificates_to_issue,
                                            convert_file_name(self.config.tree_file_pattern, self.batch_id))

        for uid, certificate in certificates_to_issue.items():
            with open(certificate.signed_certificate_file_name, 'r') as in_file:
                certificate_contents = in_file.read()
                cert_utils.print_receipt(certificate_contents, tree,
                                         convert_file_name(self.config.proof_file_pattern, uid))

        op_return_value = unhexlify(tree.merkle_root())

        unspent_outputs = wallet.get_unspent_outputs(self.issuing_address)
        last_output = unspent_outputs[-1]

        txouts = self.build_txouts(
            certificates_to_issue,
            issuing_transaction_cost,
            revocation_address)
        tx = trx_utils.create_trx(
            op_return_value,
            issuing_transaction_cost,
            self.issuing_address,
            txouts,
            last_output)

        unsigned_tx_file_name = convert_file_name(
            self.config.unsigned_txs_file_pattern, self.batch_id)
        unsent_tx_file_name = convert_file_name(
            self.config.unsent_txs_file_pattern, self.batch_id)
        sent_tx_file_name = convert_file_name(
            self.config.sent_txs_file_pattern, self.batch_id)

        td = TransactionData(uid=self.batch_id,
                             tx=tx,
                             tx_input=last_output,
                             op_return_value=hexlify(op_return_value),
                             unsigned_tx_file_name=unsigned_tx_file_name,
                             signed_tx_file_name=unsent_tx_file_name,
                             sent_tx_file_name=sent_tx_file_name)

        return [td]

    def build_txouts(self, certificates_to_issue,
                     issuing_transaction_cost, revocation_address):
        txouts = []
        for uid, certificate in certificates_to_issue.items():
            txouts = txouts + trx_utils.create_recipient_outputs(
                certificate.pubkey, revocation_address, issuing_transaction_cost.min_per_output)

        return txouts
