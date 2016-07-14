"""
About:
Signs a certificate in accordance with the open badges spec and puts it on the blockchain

How it works:
This certificate issuer assumes the existence of an unsigned, obi-compliant certificate. It signs the assertion section,
populates the signature section.

Next the certificate signature is hashed and processed as a bitcoin transaction, as follows.
1. Hash signed certificate
2. Ensure balance is available in the wallet (may involve transfering to issuing address)
3. Prepare bitcoin transaction
4. Sign bitcoin transaction
5. Send (broadcast) bitcoin transaction -- the bitcoins are not spent until this step

Transaction details:
Each certificate corresponds to a bitcoin transaction with these outputs:
1. Recipient address receives dust amount
2. Revocation address receives dust amount
3. OP_RETURN field contains signed, hashed assertion
4. Change address if the inputs are greater than above plus transaction fees

Connectors:
There are different connectors for wallets and broadcasting. By default, it uses blockchain.info for the wallet and
btc.blockr.io for broadcasting. Bitcoind connector is still under development

Use case:
This script targets a primary use case of issuing an individual certificate or a relatively small batch of
certificates (<100 -- this is for cost reasons). In the latter case there are some additional steps to speed up the
transactions by splitting into temporary addresses.

About the recipient public key:
This script assumes the recipient is assigned a public bitcoin address, located in the unsigned certificate as the
recipient pubkey field. In past certificate issuing events, this was generated in 2 ways: (1) securely generated offline
for the recipient, and (2) provided by the recipient via the certificate-viewer functionality. (1) and (2) have
different characteristics that will be discussed in a whitepaper (link TODO)

Planned changes:
- Revocation is tricky
- Debating different approach to make more economically
- Usability

"""
import sys

from cert_issuer import cert_utils
from cert_issuer import trx_utils
from cert_issuer.issuer import Issuer
from cert_issuer.models import TransactionData

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)

unsigned_tx_file_name = 'unsigned_tx.txt'
signed_tx_file_name = 'signed_tx.txt'
sent_tx_file_name = 'sent_tx.txt'


class V2Issuer(Issuer):
    def __init__(self, issuing_address):
        Issuer.__init__(self, issuing_address)

    def get_cost_for_certificate_batch(self, dust_threshold, recommended_fee_per_transaction, satoshi_per_byte,
                                       num_certificates, allow_transfer):
        """
        Per certificate, we pay 2*min_per_output (which is based on dust) + fee. Note assumes 1 input
        per tx. We may also need to pay additional fees for splitting into temp addresses
        """
        num_outputs = Issuer.get_num_outputs(num_certificates)
        return Issuer.get_cost_for_certificate_batch(dust_threshold, recommended_fee_per_transaction, satoshi_per_byte,
                                                     num_outputs, allow_transfer, 1, 1)

    def create_transactions(self, wallet, revocation_address, certificates_to_issue, issuing_transaction_cost):
        tree = cert_utils.build_merkle_tree(certificates_to_issue)
        cert_utils.build_receipts(certificates_to_issue, tree)
        op_return_value = bytes(tree.merkle_root(), 'utf-8')

        unspent_outputs = wallet.get_unspent_outputs(self.issuing_address)
        last_output = unspent_outputs[-1]

        txouts = self.build_txouts(certificates_to_issue, issuing_transaction_cost, revocation_address)
        tx = trx_utils.create_trx(op_return_value, issuing_transaction_cost, self.issuing_address, txouts, last_output)

        td = TransactionData(uid=0,  # TODO
                             tx=tx,
                             tx_input=last_output,
                             op_return_value=op_return_value,
                             unsigned_tx_file_name=unsigned_tx_file_name,
                             signed_tx_file_name=signed_tx_file_name,
                             sent_tx_file_name=sent_tx_file_name)

        return [td]

    def build_txouts(self, certificates_to_issue, issuing_transaction_cost, revocation_address):
        txouts = []
        for uid, certificate in certificates_to_issue.items():
            txouts = txouts + trx_utils.create_recipient_outputs(
                certificate.pubkey, revocation_address, issuing_transaction_cost.min_per_output)

        return txouts
