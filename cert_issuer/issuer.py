"""
Base class for building blockchain transactions to issue Blockchain Certificates.
"""
import logging
from abc import abstractmethod

from cert_issuer import trx_utils
from cert_issuer.helpers import hexlify

OUTPUTS_PER_CERTIFICATE = 2


class Issuer:
    def __init__(self, netcode, issuing_address, certificates_to_issue, connector, signer):
        self.netcode = netcode
        self.issuing_address = issuing_address
        self.certificates_to_issue = certificates_to_issue
        self.connector = connector
        self.signer = signer

    @staticmethod
    def get_num_outputs(num_certificates):
        """
        There are at most 2 additional outputs for OP_RETURN and change address
        :param num_certificates:
        :return:
        """
        return OUTPUTS_PER_CERTIFICATE * num_certificates + 2

    @staticmethod
    def get_cost_for_certificate_batch(num_outputs, allow_transfer):
        """
        Get cost for the batch of certificates
        :param num_outputs:
        :param allow_transfer:
        :return:
        """

        issuing_costs = trx_utils.get_cost(num_outputs)
        recommended_fee = trx_utils.RECOMMENDED_FEE_PER_TRANSACTION * trx_utils.COIN

        # plus additional fees for transfer
        if allow_transfer:
            issuing_costs.set_transfer_fee(recommended_fee)

        return issuing_costs

    @abstractmethod
    def validate_schema(self):
        return

    @abstractmethod
    def do_hash_certificate(self, certificate):
        """
        Subclasses must return hex strings, not byte arrays
        :param certificate: certificate to hash, byte array
        :return: hash as hex string
        """
        return

    @abstractmethod
    def create_transactions(self, revocation_address, issuing_transaction_cost):
        return

    def hash_certificates(self):
        logging.info('hashing certificates')
        for _, certificate_metadata in self.certificates_to_issue.items():
            # we need to keep the signed certificate read binary for backwards compatibility with v1
            with open(certificate_metadata.signed_cert_file_name, 'rb') as in_file, \
                    open(certificate_metadata.hashed_cert_file_name, 'w') as out_file:
                cert = in_file.read()
                hashed_cert = self.do_hash_certificate(cert)
                out_file.write(hashed_cert)

    def persist_tx(self, sent_tx_file_name, tx_id):
        with open(sent_tx_file_name, 'w') as out_file:
            out_file.write(tx_id)

    def issue_on_blockchain(self, revocation_address, issuing_transaction_cost):
        """
        Issue the certificates on the Bitcoin blockchain
        :param revocation_address:
        :param issuing_transaction_cost:
        :return:
        """
        transactions_data = self.create_transactions(revocation_address, issuing_transaction_cost)
        for transaction_data in transactions_data:
            unsigned_tx_file_name = transaction_data.batch_metadata.unsigned_tx_file_name
            signed_tx_file_name = transaction_data.batch_metadata.unsent_tx_file_name
            sent_tx_file_name = transaction_data.batch_metadata.sent_tx_file_name

            # persist the transaction in case broadcasting fails
            hex_tx = hexlify(transaction_data.tx.serialize())
            with open(unsigned_tx_file_name, 'w') as out_file:
                out_file.write(hex_tx)

            # sign transaction and persist result
            signed_tx = self.signer.sign_tx(hex_tx, transaction_data.tx_input, self.netcode)

            # log the actual byte count
            tx_byte_count = trx_utils.get_byte_count(signed_tx)
            logging.info('The actual transaction size is %d bytes', tx_byte_count)

            signed_hextx = signed_tx.as_hex()
            with open(signed_tx_file_name, 'w') as out_file:
                out_file.write(signed_hextx)

            # verify transaction before broadcasting
            trx_utils.verify_transaction(signed_hextx, transaction_data.op_return_value)

            # send tx and persist txid
            tx_id = self.connector.broadcast_tx(signed_tx)
            if tx_id:
                logging.info('Broadcast transaction with txid %s', tx_id)
            else:
                logging.warning(
                    'could not broadcast transaction but you can manually do it! signed hextx=%s', signed_hextx)

            self.persist_tx(sent_tx_file_name, tx_id)
