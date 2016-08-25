import logging
from abc import abstractmethod

from cert_issuer import cert_utils
from cert_issuer import trx_utils
from cert_issuer.helpers import hexlify
from cert_issuer.models import TotalCosts

OUTPUTS_PER_CERTIFICATE = 2


class Issuer:
    def __init__(self, config, certificates_to_issue):
        self.config = config
        self.issuing_address = config.issuing_address
        self.certificates_to_issue = certificates_to_issue

    @staticmethod
    def get_num_outputs(num_certificates):
        # worst case there are 2 additional outputs for OP_RETURN and change
        # address
        return OUTPUTS_PER_CERTIFICATE * num_certificates + 2

    @staticmethod
    def get_cost_for_certificate_batch(dust_threshold, recommended_fee_per_transaction, satoshi_per_byte,
                                       num_outputs, allow_transfer, num_transfer_outputs, num_issuing_transactions):

        issuing_costs = trx_utils.get_cost(recommended_fee_per_transaction, dust_threshold, satoshi_per_byte,
                                           num_outputs)

        # plus additional fees for transfer
        if allow_transfer:
            transfer_costs = trx_utils.get_cost(recommended_fee_per_transaction, dust_threshold, satoshi_per_byte,
                                                num_transfer_outputs)
        else:
            transfer_costs = None

        return TotalCosts(num_issuing_transactions,
                          issuing_transaction_cost=issuing_costs, transfer_cost=transfer_costs)

    @abstractmethod
    def do_hash_certificate(self, certificate):
        """
        Subclasses must return hex strings, not byte arrays
        :param certificate: certificate to hash, byte array
        :return: hash as hex string
        """
        return

    @abstractmethod
    def create_transactions(self, wallet, revocation_address, issuing_transaction_cost,
                            transfer_from_storage_address):
        return

    def hash_certificates(self):
        logging.info('hashing certificates')
        for uid, certificate_metadata in self.certificates_to_issue.items():
            # we need to keep the signed certificate read binary for backwards compatibility with v1
            with open(certificate_metadata.signed_certificate_file_name, 'rb') as in_file, \
                    open(certificate_metadata.certificate_hash_file_name, 'w') as out_file:
                cert = in_file.read()
                hashed_cert = self.do_hash_certificate(cert)
                out_file.write(hashed_cert)

    def finish_tx(self, sent_tx_file_name, txid):
        with open(sent_tx_file_name, 'w') as out_file:
            out_file.write(txid)

    def issue_on_blockchain(self, wallet, revocation_address, split_input_trxs,
                            allowable_wif_prefixes, broadcast_function, issuing_transaction_cost):

        trxs = self.create_transactions(wallet, revocation_address, issuing_transaction_cost,
                                        split_input_trxs)
        for td in trxs:
            # persist tx
            hextx = hexlify(td.tx.serialize())
            with open(td.unsigned_tx_file_name, 'w') as out_file:
                out_file.write(hextx)

            # sign transaction and persist result
            signed_hextx = trx_utils.sign_tx(
                hextx, td.tx_input, allowable_wif_prefixes)
            with open(td.signed_tx_file_name, 'w') as out_file:
                out_file.write(signed_hextx)

            # verify
            cert_utils.verify_transaction(td.op_return_value, signed_hextx)

            # send tx and persist txid
            txid = trx_utils.send_tx(broadcast_function, signed_hextx)
            self.finish_tx(td.sent_tx_file_name, txid)
