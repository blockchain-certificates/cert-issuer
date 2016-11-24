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
In V1.1 each certificate corresponded to a Bitcoin transaction. In V1.2 all certificates are batched into a single
Bitcoin transaction. The batch size limit is derived from the max transaction size (100KB) -- estimated around 2K
certificates.

1. Recipient address receives dust amount
    - in V1.1 there was 1 recipient address per transaction (and there is 1 transaction per certificate)
    - in V1.2, this is an recipient address per certificate; multiple per transaction
2. Revocation address receives dust amount
    - in V1.1, the issuer reused its revocation address since the transactions are per recipient
    - in V1.2, the issuer needs a different revocation address per recipient
3. OP_RETURN field
    - in V1.1, this contained the SHA256 digest of the hashed signed certificate
    - in V1.2, this contains the SHA256 digest of the Merkle root of a tree formed by the hashed signed certificate.
4. Change address if the inputs are greater than above plus transaction fees

Connectors:
There are different connectors for wallets and broadcasting. By default, it uses the Bitcoin wallet connector (in
 regtest mode) and btc.blockr.io for broadcasting.

Costs:
Both V1.1 and V1.2 depend on the number of certificates issued, but the multiplier is lower in V1.2. This is because
V1.1 has [num_certificate] transactions, whereas V1.2 has 1 transaction with [num_certificate] outputs. TODO: give
current estimate and examples

About the recipient public key:
This script assumes the recipient is assigned a public bitcoin address, located in the unsigned certificate as the
recipient publicKey field. The recipient provides this via the certificate wallet or certificate viewer.

"""
import glob
import logging
import os
import shutil
import sys

from cert_issuer import helpers
from cert_issuer.batch_issuer import BatchIssuer
from cert_issuer.connectors import ServiceProviderConnector
from cert_issuer.errors import NoCertificatesFoundError, NonemptyOutputDirectoryError
from cert_issuer.secure_signing import Signer, FileSecretManager
from cert_issuer.secure_signing import verify_signature

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def main(app_config):
    unsigned_certs_dir = app_config.unsigned_certificates_dir
    signed_certs_dir = app_config.signed_certificates_dir
    work_dir = app_config.work_dir
    blockcerts_dir = app_config.blockchain_certificates_dir

    blockcerts_file_pattern = str(os.path.join(blockcerts_dir, '*.json'))
    if os.path.exists(blockcerts_dir) and glob.glob(blockcerts_file_pattern):
        message = "The output directory {} is not empty. Make sure you have cleaned up results from your previous run".format(signed_certs_dir)
        logging.warning(message)
        raise NonemptyOutputDirectoryError(message)

    # delete previous work_dir contents
    for item in os.listdir(work_dir):
        file_path = os.path.join(work_dir, item)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

    # find certificates to issue
    certificates = helpers.find_certificates_to_process(unsigned_certs_dir, signed_certs_dir)
    if not certificates:
        logging.warning('No certificates to process')
        raise NoCertificatesFoundError('No certificates to process')

    certificates, batch_metadata = helpers.prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir, work_dir)
    logging.info('Processing %d certificates under work path=%s', len(certificates), work_dir)

    issuing_address = app_config.issuing_address
    revocation_address = app_config.revocation_address

    if app_config.wallet_connector_type == 'blockchain.info':
        wallet_credentials = {
            'wallet_guid': app_config.wallet_guid,
            'wallet_password': app_config.wallet_password,
            'api_key': app_config.api_key,
        }
    else:
        wallet_credentials = {}

    connector = ServiceProviderConnector(app_config.netcode, app_config.wallet_connector_type, wallet_credentials)
    path_to_secret = os.path.join(app_config.usb_name, app_config.key_file)

    signer = Signer(FileSecretManager(path_to_secret=path_to_secret, disable_safe_mode=app_config.safe_mode))

    issuer = BatchIssuer(netcode=app_config.netcode,
                         issuing_address=issuing_address,
                         certificates_to_issue=certificates,
                         connector=connector,
                         signer=signer,
                         batch_metadata=batch_metadata)




    issuer.validate_schema()

    # verify signed certs are signed with issuing key
    [verify_signature(uid, cert.signed_cert_file_name, issuing_address) for uid, cert in
     certificates.items()]

    logging.info('Hashing signed certificates.')
    issuer.hash_certificates()

    # calculate transaction costs
    all_costs = issuer.get_cost_for_certificate_batch(app_config.transfer_from_storage_address)

    logging.info('Total cost will be %d satoshis', all_costs.total)

    if app_config.transfer_from_storage_address:
        # ensure there is enough in our wallet at the storage/issuing address, transferring from the storage address
        # if configured
        logging.info('Checking there is enough balance in the issuing address')
        funds_needed = connector.check_balance_no_throw(issuing_address, all_costs)
        if funds_needed > 0:
            connector.check_balance(app_config.storage_address, all_costs)
            connector.pay(
                app_config.storage_address,
                issuing_address,
                all_costs.min_per_output,
                all_costs.fee)

    # ensure the issuing address now has sufficient balance
    connector.check_balance(issuing_address, all_costs)

    # issue the certificates on the blockchain
    logging.info('Issuing the certificates on the blockchain')
    issuer.issue_on_blockchain(revocation_address=revocation_address,
                               issuing_transaction_cost=all_costs)

    blockcerts_tmp_dir = os.path.join(work_dir, 'blockchain_certificates')
    if blockcerts_tmp_dir != blockcerts_dir:
        if not os.path.exists(blockcerts_dir):
            os.makedirs(blockcerts_dir)
        for item in os.listdir(blockcerts_tmp_dir):
            s = os.path.join(blockcerts_tmp_dir, item)
            d = os.path.join(blockcerts_dir, item)
            shutil.copy2(s, d)

    logging.info('Your Blockchain Certificates are in %s', blockcerts_dir)
    return blockcerts_dir


if __name__ == '__main__':
    from cert_issuer import config

    try:
        parsed_config = config.get_config()
        main(parsed_config)
    except Exception as ex:
        logging.error(ex, exc_info=True)
        exit(1)
