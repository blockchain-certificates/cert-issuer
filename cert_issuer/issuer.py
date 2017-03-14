"""
Base class for building blockchain transactions to issue Blockchain Certificates.
"""
import json
import logging

from chainpoint.chainpoint import MerkleTools

from cert_issuer import certificate_handler
from cert_issuer import tx_utils
from cert_issuer.errors import InsufficientFundsError
from cert_issuer.helpers import unhexlify, hexlify
from cert_issuer.secure_signer import FinalizableSigner


class Issuer:
    def __init__(self, issuing_address, certificates_to_issue, connector, secure_signer, certificate_handler,
                 transaction_handler):
        self.issuing_address = issuing_address
        self.certificates_to_issue = certificates_to_issue
        self.connector = connector
        self.secure_signer = secure_signer
        self.certificate_handler = certificate_handler
        self.transaction_handler = transaction_handler
        self.tree = MerkleTools(hash_type='sha256')

    def get_certificate_to_issue(self, uid):
        return self.certificate_handler.get_certificate_to_issue(uid)

    def validate_batch(self):
        """
        Propagates exception on failure
        :return:
        """
        for _, certificate in self.certificates_to_issue.items():
            with open(certificate.unsigned_cert_file_name) as cert:
                certificate_json = json.load(cert)
                self.certificate_handler.validate(certificate_json)

    def calculate_cost_for_certificate_batch(self):
        return self.transaction_handler.calculate_cost_for_certificate_batch()

    def sign_certificates(self):
        with FinalizableSigner(self.secure_signer) as signer:
            for _, certificate in self.certificates_to_issue.items():
                with open(certificate.unsigned_cert_file_name, 'r') as cert, \
                        open(certificate.signed_cert_file_name, 'w') as signed_cert_file:
                    certificate_json = json.load(cert)
                    to_sign = self.certificate_handler.get_message_to_sign(certificate_json)
                    signature = signer.sign_message(to_sign)
                    result = self.certificate_handler.combine_signature_with_certificate(certificate_json, signature)
                    signed_cert_file.write(result)

    def prepare_batch(self):
        for uid, certificate in self.certificates_to_issue.items():
            cert_json = self.certificate_handler.get_certificate_to_issue(uid)
            normalized = certificate_handler.normalize_jsonld(cert_json)
            hashed = certificate_handler.hash_normalized_jsonld(normalized)
            self.tree.add_leaf(hashed, False)

    def issue_on_blockchain(self):
        """
        Issue the certificates on the Bitcoin blockchain
        :param revocation_address:
        :return:
        """

        self.tree.make_tree()
        op_return_value_bytes = unhexlify(self.tree.get_merkle_root())
        op_return_value = hexlify(op_return_value_bytes)
        spendables = self.connector.get_unspent_outputs(self.issuing_address)
        if not spendables:
            error_message = 'No money to spend at address {}'.format(self.issuing_address)
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
        if tx_id:
            logging.info('Broadcast transaction with txid %s', tx_id)
        else:
            logging.warning(
                'could not broadcast transaction but you can manually do it! signed hextx=%s', signed_hextx)

        return tx_id

    def finish_batch(self, tx_id):
        root = self.tree.get_merkle_root()
        index = 0
        for uid, metadata in self.certificates_to_issue.items():
            proof = self.tree.get_proof(index)
            target_hash = self.tree.get_leaf(index)

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

            certificate_json = self.certificate_handler.get_certificate_to_issue(uid)
            blockchain_certificate = self.certificate_handler.create_receipt(uid, merkle_proof, certificate_json)
            with open(metadata.blockchain_cert_file_name, 'w') as out_file:
                out_file.write(json.dumps(blockchain_certificate))

            index += 1
