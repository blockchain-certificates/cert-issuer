"""
About:
Issues a signed certificate (see sign_certificates.py) on the blockchain

V2 Highlights:
The cost of issuing a batch of certificates has been lowered in V2 by issuing a batch of certificates as a single
Bitcoin transaction. This is achieved by forming a Merkle tree of the hashed signed certificates, and placing that
Merkle root on the blockchain.

We use the chainpoint library (https://github.com/chainpoint/chainpoint) for building the Merkle tree.

Steps:
1. Checks that there are signed certificates available to process
2. Hash signed certificate
3. Ensure balance is available in the wallet (may involve transferring to issuing address)
    - In v1 this can optionally involve splitting the transfer transaction outputs to different addresses, to more
    quickly issue the batch of certificates
4. Prepare payload to put on the blockchain in the OP_RETURN field
5. Create the Bitcoin transaction
6. Sign bitcoin transaction
7. Send (broadcast) Bitcoin transaction -- the Bitcoins are not spent until this step

Transaction Details:
In V1 each certificate corresponds to a Bitcoin transaction. In V2 all certificates are batched into a single Bitcoin
transaction. The V2 batch size limit is derived from the max transaction size (100KB) -- estimated around 2K
certificates.

1. Recipient address receives dust amount
    - in V1 there is 1 recipient address per transaction (and there is 1 transaction per certificate)
    - in V2, this is an recipient address per certificate; multiple per transaction
2. Revocation address receives dust amount
    - in V1, the issuer can reuse its revocation address since the transactions are per recipient
    - in V2, the issuer needs a different revocation address per recipient
3. OP_RETURN field
    - in V1, this contains the SHA256 digest of the hashed signed certificate
    - in V2, this contain the SHA256 digest of the Merkle root of a tree formed by the hashed signed certificate.
4. Change address if the inputs are greater than above plus transaction fees

Connectors:
There are different connectors for wallets and broadcasting. By default, it uses the Bitcoin wallet connector (in
 regtest mode) and btc.blockr.io for broadcasting.

Use case:
V1 targets a primary use case of issuing an individual certificate or a relatively small batch of certificates (<100 --
this is for cost reasons). V2 can handle larger batches more economically.

Costs:
Both V1 and V2 depend on the number of certificates issued, but the multiplier is lower in V2. This is because V1 has
[num_certificate] transactions, whereas V2 1 transaction with [num_certificate] outputs. TODO: give current estimates
and examples

About the recipient public key:
This script assumes the recipient is assigned a public bitcoin address, located in the unsigned certificate as the
recipient pubkey field. In past certificate issuing events, this was generated in 2 ways: (1) securely generated offline
for the recipient, and (2) provided by the recipient via the certificate-viewer functionality.

"""
import collections
import json
import logging
import sys

import glob2
from cert_schema.schema_tools import schema_validator

from cert_issuer import cert_utils
from cert_issuer import connectors
from cert_issuer import helpers
from cert_issuer.models import CertificateMetadata
from cert_issuer.v2_issuer import V2Issuer
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
            certificate_metadata = CertificateMetadata(app_config,
                                                       uid,
                                                       cert_json['recipient']['pubkey'])
            cert_info[uid] = certificate_metadata

    return cert_info


def main(app_config):

    # find certificates to process
    certificates = find_signed_certificates(app_config)
    if not certificates:
        logging.info('No certificates to process')
        exit(0)

    logging.info('Processing %d certificates', len(certificates))

    # get issuing and revocation addresses from config
    issuing_address = app_config.issuing_address
    revocation_address = app_config.revocation_address

    issuer = V2Issuer(config=app_config, certificates_to_issue=certificates)

    # ensure certificates are valid v1.2 schema
    for uid, certificate in certificates.items():
        with open(certificate.signed_certificate_file_name) as cert:
            cert_json = json.load(cert)
            schema_validator.validate_unsigned_v1_2_0(cert_json)

    # verify signed certs are signed with issuing key
    [cert_utils.verify_signature(uid, cert.signed_certificate_file_name, issuing_address) for uid, cert in
     certificates.items()]

    allowable_wif_prefixes = app_config.allowable_wif_prefixes

    # configure bitcoin wallet and broadcast connectors
    wallet = Wallet(connectors.create_wallet_connector(app_config))
    broadcast_function = connectors.create_broadcast_function(app_config)

    start_time = str(helpers.get_current_time_ms())

    logging.info('Hashing signed certificates.')
    issuer.hash_certificates()

    # calculate transaction costs
    all_costs = issuer.get_cost_for_certificate_batch(app_config.dust_threshold,
                                                      app_config.tx_fee,
                                                      app_config.satoshi_per_byte,
                                                      app_config.transfer_from_storage_address)

    logging.info('Total cost will be %d satoshis', all_costs.total)

    split_input_trxs = False
    if app_config.transfer_from_storage_address:
        # ensure there is enough in our wallet at the storage/issuing address, transferring from the storage address
        # if configured
        logging.info('Checking there is enough balance in the issuing address')
        funds_needed = wallet.calculate_funds_needed(
            issuing_address, all_costs)
        if funds_needed > 0:
            wallet.check_balance(app_config.storage_address, all_costs)
            wallet.transfer_balance(
                app_config.storage_address,
                issuing_address,
                all_costs.transfer_cost)
            split_input_trxs = True

    # ensure the issuing address now has sufficient balance
    wallet.check_balance(issuing_address, all_costs.issuing_transaction_cost)

    # issue the certificates on the blockchain
    logging.info('Issuing the certificates on the blockchain')
    issuer.issue_on_blockchain(wallet=wallet, revocation_address=revocation_address,
                               split_input_trxs=split_input_trxs,
                               allowable_wif_prefixes=allowable_wif_prefixes, broadcast_function=broadcast_function,
                               issuing_transaction_cost=all_costs.issuing_transaction_cost)

    # archive
    logging.info('Archiving signed certificates.')
    helpers.archive_files(app_config.signed_certs_file_pattern,
                          app_config.archived_signed_certs_file_pattern, start_time)

    logging.info('Archived sent transactions folder for safe keeping.')
    helpers.archive_files(app_config.sent_txs_file_pattern,
                          app_config.archived_txs_file_pattern, start_time)

    logging.info('Done!')


if __name__ == '__main__':
    from cert_issuer import config

    parsed_config = config.get_config()
    main(parsed_config)
