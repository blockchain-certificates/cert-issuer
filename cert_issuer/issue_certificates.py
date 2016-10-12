"""
About:
Issues a signed Blockchain Certificate on the Bitcoin blockchain

Highlights:
In v1.2 we reduced the cost of issuing a batch of certificates by issuing a batch as a single Bitcoin transaction. This
is achieved by forming a Merkle tree of the hashed signed certificates, and placing that Merkle root on the blockchain.

We use the merkle-proofs library (https://github.com/blockchain-certificates/merkle-proofs) for building the Merkle tree
and generating a receipt in a Chainpoint v2 compliant format (https://www.chainpoint.org/)

Steps:
1. Checks that there are signed certificates available to process
2. Hash signed certificates
3. Ensure balance is available in the wallet (may involve transferring to issuing address)
4. Prepare payload to put on the blockchain in the OP_RETURN field
5. Create the Bitcoin transaction
6. Sign bitcoin transaction
7. Send (broadcast) Bitcoin transaction -- the Bitcoins are not spent until this step
8. Generate receipts per recipient so the Blockchain Certificate can be verified.

Transaction Details:
In V1.1 each certificate corresponds to a Bitcoin transaction. In V1.2 all certificates are batched into a single
Bitcoin transaction. The V1.2 batch size limit is derived from the max transaction size (100KB) -- estimated around 2K
certificates.

1. Recipient address receives dust amount
    - in V1.1 there is 1 recipient address per transaction (and there is 1 transaction per certificate)
    - in V1.2, this is an recipient address per certificate; multiple per transaction
2. Revocation address receives dust amount
    - in V1.1, the issuer can reuse its revocation address since the transactions are per recipient
    - in V1.2, the issuer needs a different revocation address per recipient
3. OP_RETURN field
    - in V1.1, this contains the SHA256 digest of the hashed signed certificate
    - in V1.2, this contains the SHA256 digest of the Merkle root of a tree formed by the hashed signed certificate.
4. Change address if the inputs are greater than above plus transaction fees

Connectors:
There are different connectors for wallets and broadcasting. By default, it uses the Bitcoin wallet connector (in
 regtest mode) and btc.blockr.io for broadcasting.

Use case:
V1.1 targets a primary use case of issuing an individual certificate or a relatively small batch of certificates (<100--
this is for cost reasons). V1.2 can handle larger batches more economically.

Costs:
Both V1.1 and V1.2 depend on the number of certificates issued, but the multiplier is lower in V1.2. This is because
V1.1 has [num_certificate] transactions, whereas V1.2 has 1 transaction with [num_certificate] outputs. TODO: give
current estimate and examples

About the recipient public key:
This script assumes the recipient is assigned a public bitcoin address, located in the unsigned certificate as the
recipient publicKey field. In past certificate issuing events, this was generated in 2 ways: (1) securely generated
offline for the recipient, and (2) provided by the recipient via the certificate-viewer functionality.

"""
import collections
import json
import logging
import os
import sys

import glob2

from cert_issuer import cert_utils
from cert_issuer import helpers
from cert_issuer.batch_issuer import BatchIssuer
from cert_issuer.models import CertificateMetadata
from cert_issuer.wallet import Wallet

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def find_signed_certificates(app_config):
    cert_info = collections.OrderedDict()
    for filename, (uid,) in sorted(glob2.iglob(
            app_config.signed_certs_file_pattern, with_matches=True)):
        with open(filename) as cert_file:
            cert_raw = cert_file.read()
            cert_json = json.loads(cert_raw)
            revocation_key = None
            if 'revocationKey' in cert_json['recipient']:
                revocation_key = cert_json['recipient']['revocationKey']
            certificate_metadata = CertificateMetadata(app_config,
                                                       uid,
                                                       cert_json['recipient']['publicKey'],
                                                       revocation_key)
            cert_info[uid] = certificate_metadata

    return cert_info


def main(app_config):
    # find certificates to process
    certificates = find_signed_certificates(app_config)
    if not certificates:
        logging.info('No certificates to process')
        exit(0)

    batch_id = helpers.get_batch_id(list(certificates.keys()))
    logging.info('Processing %d certificates with batch id=%s', len(certificates), batch_id)

    helpers.clear_intermediate_folders(app_config)

    # get issuing and revocation addresses from config
    issuing_address = app_config.issuing_address
    revocation_address = app_config.revocation_address

    issuer = BatchIssuer(config=app_config, certificates_to_issue=certificates)

    issuer.validate_schema()

    # verify signed certs are signed with issuing key
    [cert_utils.verify_signature(uid, cert.signed_certificate_file_name, issuing_address) for uid, cert in
     certificates.items()]

    allowable_wif_prefixes = app_config.allowable_wif_prefixes

    # configure bitcoin wallet and broadcast connectors
    wallet = Wallet()

    logging.info('Hashing signed certificates.')
    issuer.hash_certificates()

    # calculate transaction costs
    all_costs = issuer.get_cost_for_certificate_batch(app_config.dust_threshold,
                                                      app_config.tx_fee,
                                                      app_config.satoshi_per_byte,
                                                      app_config.transfer_from_storage_address)

    logging.info('Total cost will be %d satoshis', all_costs.total)

    if app_config.transfer_from_storage_address:
        # ensure there is enough in our wallet at the storage/issuing address, transferring from the storage address
        # if configured
        logging.info('Checking there is enough balance in the issuing address')
        funds_needed = wallet.check_balance(
            issuing_address, all_costs)
        if funds_needed > 0:
            wallet.check_balance(app_config.storage_address, all_costs)
            wallet.send_payment(
                app_config.storage_address,
                issuing_address,
                all_costs.issuing_transaction_cost.min_per_output,
                all_costs.issuing_transaction_cost.fee)

    # ensure the issuing address now has sufficient balance
    wallet.check_balance(issuing_address, all_costs.issuing_transaction_cost)

    # issue the certificates on the blockchain
    logging.info('Issuing the certificates on the blockchain')
    issuer.issue_on_blockchain(revocation_address=revocation_address,
                               allowable_wif_prefixes=allowable_wif_prefixes,
                               issuing_transaction_cost=all_costs.issuing_transaction_cost)

    # archive
    logging.info('Archiving signed certificates.')
    helpers.archive_files(app_config.signed_certs_file_pattern,
                          app_config.archive_path,
                          app_config.signed_certs_file_part,
                          batch_id)

    logging.info('Archiving sent transactions.')
    helpers.archive_files(app_config.sent_txs_file_pattern,
                          app_config.archive_path,
                          app_config.txs_file_part,
                          batch_id)

    logging.info('Archiving receipts.')
    helpers.archive_files(app_config.receipts_file_pattern,
                          app_config.archive_path,
                          app_config.receipts_file_part,
                          batch_id)

    logging.info('Archiving blockchain certificates.')
    helpers.archive_files(app_config.blockchain_certificates_file_pattern,
                          app_config.archive_path,
                          app_config.blockchain_certificates_file_part,
                          batch_id)

    archive_folder = os.path.join(app_config.archive_path, batch_id)
    logging.info('Your Blockchain Certificates are in %s', archive_folder)


if __name__ == '__main__':
    from cert_issuer import config

    parsed_config = config.get_config()
    main(parsed_config)
