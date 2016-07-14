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
import json
import logging
import sys

import glob2
from cert_issuer import cert_utils
from cert_issuer import connectors
from cert_issuer import helpers
from cert_issuer.issuer import create_issuer
from cert_issuer.models import CertificateMetadata
from cert_issuer.wallet import Wallet

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def find_signed_certificates(app_config):
    cert_info = {}
    for filename, (uid,) in glob2.iglob(app_config.signed_certs_file_pattern, with_matches=True):
        with open(filename) as cert_file:
            cert_raw = cert_file.read()
            cert_json = json.loads(cert_raw)
            certificate_metadata = CertificateMetadata(app_config,
                                                       uid,
                                                       cert_json['recipient']['pubkey'])
            cert_info[uid] = certificate_metadata

    return cert_info


def main(app_config):
    issuer = create_issuer(v2=True, issuing_address=app_config.issuing_address)

    # find certificates to process
    certificates = helpers.find_signed_certificates(app_config)
    if not certificates:
        logging.info('No certificates to process')
        exit(0)

    logging.info('Processing %d certificates', len(certificates))

    # get issuing and revocation addresses from config
    issuing_address = app_config.issuing_address
    revocation_address = app_config.revocation_address

    # verify signed certs are signed with issuing key
    [cert_utils.verify_signature(uid, cert.signed_certificate_file_name, issuing_address) for uid, cert in
     certificates.items()]

    allowable_wif_prefixes = app_config.allowable_wif_prefixes

    # configure bitcoin wallet and broadcast connectors
    wallet = Wallet(connectors.create_wallet_connector(app_config))
    broadcast_function = connectors.create_broadcast_function(app_config)

    start_time = str(helpers.get_current_time_ms())

    logging.info('Hashing signed certificates.')
    cert_utils.hash_certs(certificates)

    logging.info('Archiving signed certificates.')
    helpers.archive_files(app_config.signed_certs_file_pattern,
                          app_config.archived_certs_file_pattern, start_time)

    # TODO: sort certificates

    # calculate transaction costs
    all_costs = issuer.get_cost_for_certificate_batch(app_config.dust_threshold, app_config.tx_fee,
                                                      app_config.satoshi_per_byte, len(certificates),
                                                      app_config.transfer_from_storage_address)

    logging.info('Total cost will be %d satoshis', all_costs.total)

    if app_config.transfer_from_storage_address:
        # ensure there is enough in our wallet at the storage/issuing address, transferring from the storage address
        # if configured
        logging.info('Checking there is enough balance in the issuing address')
        funds_needed = wallet.calculate_funds_needed(issuing_address, all_costs)
        if funds_needed > 0:
            wallet.check_balance(app_config.storage_address, all_costs)
            wallet.transfer_balance(app_config.storage_address, issuing_address, all_costs.transfer_cost)

    # ensure the issuing address now has sufficient balance
    wallet.check_balance(issuing_address, all_costs.issuing_transaction_cost)

    # issue the certificates on the blockchain
    logging.info('Issuing the certificates on the blockchain')
    issuer.issue_on_blockchain(wallet, broadcast_function, revocation_address, certificates,
                               all_costs.issuing_transaction_cost, allowable_wif_prefixes)

    # archive
    logging.info('Archived sent transactions folder for safe keeping.')
    helpers.archive_files(app_config.sent_txs_file_pattern,
                          app_config.archived_txs_file_pattern, start_time)

    logging.info('Done!')


if __name__ == '__main__':
    from cert_issuer import config

    parsed_config = config.get_config()
    main(parsed_config)
