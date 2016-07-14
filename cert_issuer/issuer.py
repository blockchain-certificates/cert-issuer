from abc import abstractmethod
from cert_issuer import cert_utils
from cert_issuer import trx_utils
from cert_issuer.helpers import hexlify
from cert_issuer.models import AllCosts
from cert_issuer.v1_issuer import V1Issuer
from cert_issuer.v2_issuer import V2Issuer

OUTPUTS_PER_CERTIFICATE = 2


class Issuer:
    def __init__(self, issuing_address):
        self.issuing_address = issuing_address

    @staticmethod
    def get_num_outputs(num_certificates):
        # worst case there are 2 additional outputs for OP_RETURN and change address
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

        return AllCosts(num_issuing_transactions, issuing_transaction_cost=issuing_costs, transfer_costs=transfer_costs)

    @abstractmethod
    def create_transactions(self):
        return

    def issue_on_blockchain(self, wallet, revocation_address, certificates_to_issue, transfer_from_storage_address,
                            allowable_wif_prefixes, broadcast_function, issuing_transaction_cost):

        trxs = self.create_transactions(wallet, revocation_address, certificates_to_issue, issuing_transaction_cost,
                                        transfer_from_storage_address)
        for td in trxs:
            # persist tx
            hextx = hexlify(td.tx.serialize())
            with open(td.unsigned_tx_file_name, 'wb') as out_file:
                out_file.write(bytes(hextx, 'utf-8'))

            # sign transaction and persist result
            signed_hextx = trx_utils.sign_tx(hextx, td.tx_input, allowable_wif_prefixes)
            with open(td.signed_tx_file_name, 'wb') as out_file:
                out_file.write(bytes(signed_hextx, 'utf-8'))

            # verify
            cert_utils.verify_transaction(td.op_return_value, signed_hextx)

            # send tx and persist txid
            txid = trx_utils.send_tx(broadcast_function, td.signed_tx_file_name, td.sent_tx_file_name)
            with open(td.sent_tx_file_name, 'wb') as out_file:
                out_file.write(bytes(txid, 'utf-8'))


def create_issuer(v2, issuing_address):
    if v2:
        return V2Issuer(issuing_address)
    return V1Issuer(issuing_address)
