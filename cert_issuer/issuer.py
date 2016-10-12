"""
Base class for building blockchain transactions to issue Blockchain Certificates.
"""
import logging
from abc import abstractmethod

from cert_issuer import config
from cert_issuer import trx_utils
from cert_issuer.connectors import broadcast_tx
from cert_issuer.helpers import hexlify

OUTPUTS_PER_CERTIFICATE = 2

cost_constants = config.get_constants()
recommended_fee = cost_constants.recommended_fee_per_transaction * trx_utils.COIN


class Issuer:
    def __init__(self, config, certificates_to_issue):
        self.config = config
        self.issuing_address = config.issuing_address
        self.certificates_to_issue = certificates_to_issue

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
            with open(certificate_metadata.signed_certificate_file_name, 'rb') as in_file, \
                    open(certificate_metadata.certificate_hash_file_name, 'w') as out_file:
                cert = in_file.read()
                hashed_cert = self.do_hash_certificate(cert)
                out_file.write(hashed_cert)

    def finish_tx(self, sent_tx_file_name, txid):
        with open(sent_tx_file_name, 'w') as out_file:
            out_file.write(txid)

    def issue_on_blockchain(self, revocation_address, issuing_transaction_cost):
        """
        Issue the certificates on the Bitcoin blockchain
        :param revocation_address:
        :param issuing_transaction_cost:
        :return:
        """
        trxs = self.create_transactions(revocation_address, issuing_transaction_cost)
        for td in trxs:
            # persist the transaction in case broadcasting fails
            hextx = hexlify(td.tx.serialize())
            with open(td.unsigned_tx_file_name, 'w') as out_file:
                out_file.write(hextx)

            # sign transaction and persist result
            signed_tx = trx_utils.sign_tx(hextx, td.tx_input)
            signed_hextx = signed_tx.as_hex()
            with open(td.signed_tx_file_name, 'w') as out_file:
                out_file.write(signed_hextx)

            # verify
            trx_utils.verify_transaction(signed_hextx, td.op_return_value)

            # send tx and persist txid
            txid = broadcast_tx(signed_tx)
            if txid:
                logging.info('Broadcast transaction with txid %s', txid)
            else:
                logging.warning(
                    'could not broadcast transaction but you can manually do it! signed hextx=%s', signed_hextx)

            self.finish_tx(td.sent_tx_file_name, txid)
