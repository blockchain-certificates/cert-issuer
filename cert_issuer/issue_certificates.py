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
3. Ensure balance is available in the wallet
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
import logging
import os
import shutil
import sys

from cert_issuer import helpers
from cert_issuer import secure_signer
from cert_issuer.batch_issuer import BatchIssuer
from cert_issuer.connectors import ServiceProviderConnector
from cert_issuer.errors import NoCertificatesFoundError, InsufficientFundsError
from cert_issuer.secure_signer import Signer
from cert_issuer.tx_utils import TransactionCostConstants

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def main(app_config, secret_manager=None):
    unsigned_certs_dir = app_config.unsigned_certificates_dir
    signed_certs_dir = app_config.signed_certificates_dir
    blockcerts_dir = app_config.blockchain_certificates_dir
    work_dir = app_config.work_dir

    # find certificates to issue
    certificates = helpers.find_certificates_to_process(unsigned_certs_dir, signed_certs_dir)
    if not certificates:
        logging.warning('No certificates to process')
        raise NoCertificatesFoundError('No certificates to process')

    certificates, batch_metadata = helpers.prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir, work_dir)
    logging.info('Processing %d certificates under work path=%s', len(certificates), work_dir)

    issuing_address = app_config.issuing_address
    revocation_address = app_config.revocation_address

    connector = ServiceProviderConnector(app_config.bitcoin_chain, app_config.netcode)

    if not secret_manager:
        secret_manager = secure_signer.initialize_secret_manager(app_config)
    signer = Signer(secret_manager)

    tx_constants = TransactionCostConstants(app_config.tx_fee, app_config.dust_threshold, app_config.satoshi_per_byte)

    issuer = BatchIssuer(netcode=app_config.netcode,
                         issuing_address=issuing_address,
                         certificates_to_issue=certificates,
                         connector=connector,
                         signer=signer,
                         tx_cost_constants=tx_constants,
                         batch_metadata=batch_metadata)

    issuer.validate_schema()

    # verify signed certs are signed with issuing key
    [secure_signer.verify_signature(uid, cert.signed_cert_file_name, issuing_address) for uid, cert in
     certificates.items()]

    logging.info('Hashing signed certificates.')
    issuer.hash_certificates()

    # calculate transaction cost
    transaction_cost = issuer.calculate_cost_for_certificate_batch()

    logging.info('Total cost will be %d satoshis', transaction_cost)

    # ensure the issuing address has sufficient balance
    balance = connector.get_balance(issuing_address)

    if transaction_cost > balance:
        error_message = 'Please add {} satoshis to the address {}'.format(
            transaction_cost - balance, issuing_address)
        logging.error(error_message)
        raise InsufficientFundsError(error_message)

    # issue the certificates on the blockchain
    logging.info('Issuing the certificates on the blockchain')
    txid = issuer.issue_on_blockchain(revocation_address=revocation_address)
    logging.info('Transaction id=%s', txid)

    blockcerts_tmp_dir = os.path.join(work_dir, helpers.BLOCKCHAIN_CERTIFICATES_DIR)
    if not os.path.exists(blockcerts_dir):
        os.makedirs(blockcerts_dir)
    for item in os.listdir(blockcerts_tmp_dir):
        s = os.path.join(blockcerts_tmp_dir, item)
        d = os.path.join(blockcerts_dir, item)
        shutil.copy2(s, d)

    logging.info('Your Blockchain Certificates are in %s', blockcerts_dir)
    return txid


if __name__ == '__main__':
    from cert_issuer import config

    try:
        parsed_config = config.get_config()
        main(parsed_config)
    except Exception as ex:
        logging.error(ex, exc_info=True)
        exit(1)
