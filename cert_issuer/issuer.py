"""
Base class for building blockchain transactions to issue Blockchain Certificates.
"""
import logging

from chainpoint.chainpoint import MerkleTools

from cert_issuer import tx_utils
from cert_issuer.errors import InsufficientFundsError, BroadcastError
from cert_issuer.helpers import unhexlify, hexlify
from cert_issuer.secure_signer import FinalizableSigner


class Issuer:
    def __init__(self, connector, secure_signer, certificate_batch_handler, transaction_handler, max_retry=10):
        self.connector = connector
        self.secure_signer = secure_signer
        self.certificate_batch_handler = certificate_batch_handler
        self.transaction_handler = transaction_handler
        self.max_retry = max_retry
        self.tree = MerkleTools(hash_type='sha256')

    def calculate_cost_for_certificate_batch(self):
        return self.transaction_handler.calculate_cost_for_certificate_batch()

    def sign_batch(self):
        with FinalizableSigner(self.secure_signer) as signer:
            self.certificate_batch_handler.sign_batch(signer)

    def prepare_batch(self):
        node_generator = self.certificate_batch_handler.create_node_generator()
        for node in node_generator:
            self.tree.add_leaf(node, False)

    def issue_on_blockchain(self):
        """
        Issue the certificates on the Bitcoin blockchain
        :param revocation_address:
        :return:
        """

        self.tree.make_tree()
        op_return_value_bytes = unhexlify(self.tree.get_merkle_root())
        op_return_value = hexlify(op_return_value_bytes)

        for attempt_number in range(0, self.max_retry):
            try:
                spendables = self.connector.get_unspent_outputs(self.secure_signer.issuing_address)
                if not spendables:
                    error_message = 'No money to spend at address {}'.format(self.secure_signer.issuing_address)
                    logging.error(error_message)
                    raise InsufficientFundsError(error_message)

                last_input = spendables[-1]

                tx = self.transaction_handler.create_transaction(last_input, op_return_value_bytes)

                hex_tx = hexlify(tx.serialize())
                logging.info('Unsigned hextx=%s', hex_tx)

                prepared_tx = tx_utils.prepare_tx_for_signing(hex_tx, [last_input])
                with FinalizableSigner(self.secure_signer) as signer:
                    signed_tx = signer.sign_transaction(prepared_tx)

                # log the actual byte count
                tx_byte_count = tx_utils.get_byte_count(signed_tx)
                logging.info('The actual transaction size is %d bytes', tx_byte_count)

                signed_hextx = signed_tx.as_hex()
                logging.info('Signed hextx=%s', signed_hextx)

                # verify transaction before broadcasting
                tx_utils.verify_transaction(signed_hextx, op_return_value)

                # send tx and persist txid
                tx_id = self.connector.broadcast_tx(signed_tx)
                logging.info('Broadcast transaction with txid %s', tx_id)
                return tx_id
            except BroadcastError:
                logging.warning(
                    'Failed broadcast reattempts. Trying to recreate transaction. This is attempt number %d', attempt_number)
        logging.error('All attempts to broadcast failed. Try rerunning issuer.')
        return None

    def finish_batch(self, tx_id):
        def create_proof_generator(tree):
            root = tree.get_merkle_root()
            node_count = len(tree.leaves)
            for index in range(0, node_count):
                proof = tree.get_proof(index)
                target_hash = tree.get_leaf(index)
                merkle_proof = {
                    "@context": "https://w3id.org/chainpoint/v2",
                    "type": "ChainpointSHA256v2",
                    "merkleRoot": root,
                    "targetHash": target_hash,
                    "proof": proof,
                    "anchors": [{
                        "sourceId": tx_id,
                        "type": "BTCOpReturn"
                    }]}
                yield merkle_proof

        self.certificate_batch_handler.add_proofs(create_proof_generator, self.tree)

    def issue_certificates(self):
        logging.info('Preparing certificate batch')
        self.certificate_batch_handler.validate_batch()

        logging.info('Signing certificates')
        self.sign_batch()

        logging.info('Preparing certificate batch')
        self.prepare_batch()

        logging.info('Issuing the certificates on the blockchain')
        tx_id = self.issue_on_blockchain()

        logging.info('Finishing batch with txid=%s', tx_id)
        self.finish_batch(tx_id)
        return tx_id
