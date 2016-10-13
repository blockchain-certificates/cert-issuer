import json
import logging
import random

from cert_schema.schema_tools import schema_validator
from merkleproof.MerkleTree import MerkleTree
from merkleproof.MerkleTree import sha256
from pyld import jsonld

from cert_issuer import trx_utils
from cert_issuer.connectors import get_unspent_outputs
from cert_issuer.errors import InsufficientFundsError
from cert_issuer.helpers import unhexlify, hexlify
from cert_issuer.issuer import Issuer
from cert_issuer.models import TransactionData
from cert_issuer.models import convert_file_name


class BatchIssuer(Issuer):
    def __init__(self, config, certificates_to_issue):
        Issuer.__init__(self, config, certificates_to_issue)
        self.batch_id = '%024x' % random.randrange(16 ** 24)
        self.tree = MerkleTree(hash_f=sha256)

    def validate_schema(self):
        """
        Ensure certificates are valid v1.2 schema
        :return:
        """
        for _, certificate in self.certificates_to_issue.items():
            with open(certificate.signed_certificate_file_name) as cert:
                cert_json = json.load(cert)
                schema_validator.validate_unsigned_v1_2(cert_json)

    def do_hash_certificate(self, certificate):
        """
        Hash the JSON-LD normalized certificate
        :param certificate:
        :return:
        """
        cert_utf8 = certificate.decode('utf-8')
        cert_json = json.loads(cert_utf8)
        normalized = jsonld.normalize(cert_json, {'algorithm': 'URDNA2015', 'format': 'application/nquads'})
        hashed = sha256(normalized)
        self.tree.add_leaf(hashed, False)
        return hashed

    def get_cost_for_certificate_batch(self, allow_transfer):
        """
        Per certificate, we pay 2*min_per_output (which is based on dust) + fee. Note assumes 1 input
        per tx. We may also need to pay additional fees for splitting into temp addresses
        :param allow_transfer:
        :return:
        """
        num_certificates = len(self.certificates_to_issue)
        num_outputs = Issuer.get_num_outputs(num_certificates)
        return Issuer.get_cost_for_certificate_batch(num_outputs, allow_transfer)

    def finish_tx(self, sent_tx_file_name, tx_id):
        Issuer.finish_tx(self, sent_tx_file_name, tx_id)
        # note that certificates are stored in an ordered dictionary, so we will iterate in the same order
        index = 0
        for uid, _ in self.certificates_to_issue.items():
            receipt = self.tree.make_receipt(index, tx_id)

            receipt_file_name = convert_file_name(self.config.receipts_file_pattern, uid)
            with open(receipt_file_name, 'w') as out_file:
                out_file.write(json.dumps(receipt))

            signed_cert_file_name = convert_file_name(self.config.signed_certs_file_pattern, uid)
            with open(signed_cert_file_name, 'r') as in_file:
                signed_cert = json.load(in_file)

            blockchain_cert = {
                '@context': 'https://w3id.org/blockcerts/v1',
                'type': 'BlockchainCertificate',
                'document': signed_cert,
                'receipt': receipt
            }
            blockchain_cert_file_name = convert_file_name(self.config.blockchain_certificates_file_pattern, uid)

            with open(blockchain_cert_file_name, 'w') as out_file:
                out_file.write(json.dumps(blockchain_cert))

            index += 1

    def create_transactions(self, revocation_address, issuing_transaction_cost):
        """
        Create the batch Bitcoin transaction
        :param revocation_address:
        :param issuing_transaction_cost:
        :return:
        """
        self.tree.make_tree()

        spendables = get_unspent_outputs(self.issuing_address)
        if not spendables:
            error_message = 'No money to spend at address {}'.format(self.issuing_address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

        last_input = spendables[-1]

        op_return_value = unhexlify(self.tree.get_merkle_root())

        tx_outs = self.build_recipient_tx_outs()
        tx_outs.append(trx_utils.create_transaction_output(revocation_address,
                                                           issuing_transaction_cost.min_per_output))

        transaction = trx_utils.create_trx(
            op_return_value,
            issuing_transaction_cost,
            self.issuing_address,
            tx_outs,
            last_input)

        unsigned_tx_file_name = convert_file_name(self.config.unsigned_txs_file_pattern, self.batch_id)
        unsent_tx_file_name = convert_file_name(self.config.signed_txs_file_pattern, self.batch_id)
        sent_tx_file_name = convert_file_name(self.config.sent_txs_file_pattern, self.batch_id)

        transaction_data = TransactionData(uid=self.batch_id,
                                           tx=transaction,
                                           tx_input=last_input,
                                           op_return_value=hexlify(op_return_value),
                                           unsigned_tx_file_name=unsigned_tx_file_name,
                                           signed_tx_file_name=unsent_tx_file_name,
                                           sent_tx_file_name=sent_tx_file_name)

        return [transaction_data]

    def build_recipient_tx_outs(self):
        """
        Creates 2 transaction outputs for each recipient: one to their public key and the other to their specific
        revocation key.
        :return:
        """
        tx_outs = []
        for _, certificate in self.certificates_to_issue.items():
            tx_outs = tx_outs + trx_utils.create_recipient_outputs(certificate.public_key, certificate.revocation_key)

        return tx_outs
