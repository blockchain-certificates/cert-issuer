import sys

import random
from pyld import jsonld
import json
from cert_issuer import trx_utils
from cert_issuer.helpers import unhexlify, hexlify
from cert_issuer.issuer import Issuer
from cert_issuer.models import TransactionData
from cert_issuer.models import convert_file_name
from merkleproof.MerkleTree import MerkleTree
from merkleproof.MerkleTree import sha256
from merkleproof.utils import get_buffer


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
        self.tree = MerkleTree(hash_f=sha256)

    def do_hash_certificate(self, certificate):
        cert_utf8 = certificate.decode('utf-8')
        cert_json = json.loads(cert_utf8)
        normalized = jsonld.normalize(cert_json, {'algorithm': 'URDNA2015', 'format': 'application/nquads'})
        hashed_bytes = get_buffer(sha256(normalized))
        self.tree.add_leaf(hashed_bytes, True)
        return hashed_bytes

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
        # finish tree
        self.tree.make_tree()

        # convert_file_name(self.config.tree_file_pattern, self.batch_id)

        # note that certificates are stored in an ordered dictionary, so we will iterate in the same order
        index = 0
        for uid, certificate in certificates_to_issue.items():

            # TODO: fix
            receipt = {'target': hexlify(self.tree.get_leaf(index)),
                       'root': self.tree.get_merkle_root(),
                       'proof': self.tree.get_proof(index)
                       }

            receipt_file_name = convert_file_name(self.config.proof_file_pattern, uid)
            with open(receipt_file_name, 'w') as out_file:
                out_file.write(json.dumps(receipt))
            index+=1

        op_return_value = unhexlify(self.tree.get_merkle_root())

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
