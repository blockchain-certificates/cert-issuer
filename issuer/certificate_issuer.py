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

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)

import glob2
import time

import hashlib
import json
import logging
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.signmessage import BitcoinMessage, SignMessage
from bitcoin.signmessage import VerifyMessage
from bitcoin.wallet import CBitcoinAddress
from bitcoin.wallet import CBitcoinSecret
from pycoin.encoding import wif_to_secret_exponent
from pycoin.tx import Tx, TxOut
from pycoin.tx.pay_to import build_hash160_lookup

from issuer import helpers
from issuer.helpers import hexlify, internet_off_for_scope
from issuer.errors import UnverifiedDocumentError, UnverifiedSignatureError

from issuer.models import CertificateMetadata

from issuer import connectors, wallet
from issuer.wallet import Wallet


import bitcoin
bitcoin.SelectParams('regtest')

def do_sign(certificate, secret_key):
    """Signs the certificate. String input and output.
    """
    cert = json.loads(certificate)
    to_sign = cert['assertion']['uid']
    message = BitcoinMessage(to_sign)
    signature = SignMessage(secret_key, message)
    cert['signature'] = str(signature, 'utf-8')
    sorted_cert = json.dumps(cert, sort_keys=True)
    return sorted_cert


def do_verify_signature(address, signed_cert):
    signed_cert_json = json.loads(signed_cert)
    to_verify = signed_cert_json['assertion']['uid']
    message = BitcoinMessage(to_verify)
    signature = signed_cert_json['signature']
    verified = VerifyMessage(address, message, signature)
    if not verified:
        raise UnverifiedSignatureError('There was a problem with the signature for certificate uid=%s',
                                       signed_cert_json['assertion']['uid'])


def sign_and_hash_certs(certificates_metadata):
    """Consider pulling out hashing step since that isn't technically part of the open badges cert"""
    sign_certs(certificates_metadata)
    hash_certs(certificates_metadata)


@internet_off_for_scope
def sign_certs(certificates_metadata):
    """Sign certificates. Internet should be off for the scope of this function."""
    logging.info('signing certificates')
    pk = helpers.import_key()
    secret_key = CBitcoinSecret(pk)
    for uid, certificate_metadata in certificates_metadata.items():
        with open(certificate_metadata.unsigned_certificate_file_name, 'r') as cert_in, \
                open(certificate_metadata.signed_certificate_file_name, 'wb') as signed_cert:
            cert = do_sign(cert_in.read(), secret_key)
            signed_cert.write(bytes(cert, 'utf-8'))


def hash_certs(certificates_metadata):
    logging.info('hashing certificates')
    for uid, certificate_metadata in certificates_metadata.items():
        with open(certificate_metadata.signed_certificate_file_name, 'rb') as in_file, \
                open(certificate_metadata.certificate_hash_file_name, 'wb') as out_file:
            cert = in_file.read()
            hashed_cert = _hash_cert(cert)
            out_file.write(hashed_cert)


def _hash_cert(signed_certificate):
    return hashlib.sha256(signed_certificate).digest()


def issue_on_blockchain(wallet, broadcast_function, issuing_address, revocation_address,
                        certificates_to_issue, fees):
    for uid, certificate_metadata in certificates_to_issue.items():
        last_input = _build_certificate_transactions(wallet, issuing_address, revocation_address,
                                                     certificate_metadata, fees)
        # sign transaction
        sign_tx(certificate_metadata, last_input)

        # verify
        verify(certificate_metadata, issuing_address)

        # broadcast via configurable broadcast_function
        send_tx(broadcast_function, certificate_metadata)


def _build_certificate_transactions(wallet, issuing_address, revocation_address, certificate_metadata, fees):
    """Make transactions for the certificates.
    """
    logging.info('Creating tx of certificate for recipient uid: %s ...', certificate_metadata.uid)

    with open(certificate_metadata.certificate_hash_file_name, 'rb') as in_file:
        # this is the recipient-specific hash we are putting on the blockchain
        hashed_certificate = in_file.read()
        cert_out = CMutableTxOut(0, CScript([OP_RETURN, hashed_certificate]))
        # we send a transaction to the recipient's public key, and to a revocation address
        txouts = _create_recipient_outputs(certificate_metadata.pubkey, revocation_address, fees.min_per_transaction)

        # independent
        unspent_outputs = wallet.get_unspent_outputs(issuing_address)
        last_input = unspent_outputs[len(unspent_outputs) - 1]

        txins = [CTxIn(last_input.outpoint)]
        value_in = last_input.amount

        amount = value_in - fees.cost_per_transaction
        if amount > 0:
            change_out = _create_transaction_output(issuing_address, amount)
            txouts = txouts + [change_out]

        txouts = txouts + [cert_out]
        tx = CMutableTransaction(txins, txouts)

        # this is the transaction for a recipient, unsigned
        hextx = hexlify(tx.serialize())
        with open(certificate_metadata.unsigned_tx_file_name, 'wb') as out_file:
            out_file.write(bytes(hextx, 'utf-8'))

        logging.info('Created unsigned tx for recipient; last_input=%s', last_input)
        return last_input


def _create_recipient_outputs(recipient_address, revocation_address, transaction_fee):
    recipient_out = _create_transaction_output(recipient_address, transaction_fee)
    revoke_out = _create_transaction_output(revocation_address, transaction_fee)
    recipient_outs = [recipient_out] + [revoke_out]
    return recipient_outs


def _create_transaction_output(address, transaction_fee):
    addr = CBitcoinAddress(address)
    tx_out = CMutableTxOut(transaction_fee, addr.to_scriptPubKey())
    return tx_out


@internet_off_for_scope
def sign_tx(certificate_metadata, last_input):
    """sign the transaction with private key"""
    with open(certificate_metadata.unsigned_tx_file_name, 'rb') as in_file:
        hextx = str(in_file.read(), 'utf-8')

        logging.info('Signing tx with private key for recipient id: %s ...', certificate_metadata.uid)

        tx = Tx.from_hex(hextx)
        wif = wif_to_secret_exponent(helpers.import_key())
        lookup = build_hash160_lookup([wif])

        tx.set_unspents([TxOut(coin_value=last_input.amount, script=last_input.script_pub_key)])

        signed_tx = tx.sign(lookup)
        signed_hextx = signed_tx.as_hex()
        with open(certificate_metadata.unsent_tx_file_name, 'wb') as out_file:
            out_file.write(bytes(signed_hextx, 'utf-8'))

    logging.info('Finished signing transaction for certificate uid=%s', certificate_metadata.uid)


def send_tx(broadcaster, certificate_metadata):
    """broadcast the transaction, putting it on the blockchain"""
    with open(certificate_metadata.unsent_tx_file_name, 'rb') as in_file:
        hextx = str(in_file.read(), 'utf-8')
        txid = broadcaster(hextx)
        if txid:
            with open(certificate_metadata.sent_tx_file_name, 'wb') as out_file:
                out_file.write(bytes(txid, 'utf-8'))
                logging.info('Broadcast transaction for certificate id %s with a txid of %s', certificate_metadata.uid,
                             txid)
        else:
            logging.warning('could not broadcast transaction but you can manually do it! hextx=%s', hextx)


def verify(certificate_metadata, issuing_address):
    logging.info('verifying certificate with uid=%s:', certificate_metadata.uid)
    with open(certificate_metadata.signed_certificate_file_name) as in_file:
        verified_sig = do_verify_signature(issuing_address, in_file.read())
        logging.info('verified signature: %s', verified_sig)
        verified_doc = verify_doc(certificate_metadata)
        logging.info('verified OP_RETURN: %s', verified_doc)


def verify_doc(certificate_metadata):
    with open(certificate_metadata.signed_certificate_file_name, 'rb') as in_file:
        hashed_cert = hashlib.sha256(in_file.read()).hexdigest()
        unsent_tx_file_name = certificate_metadata.unsent_tx_file_name

        with open(unsent_tx_file_name) as unsent_tx_file:
            op_return_hash = unsent_tx_file.read()[-72:-8]
            result = (hashed_cert == op_return_hash)
            if not result:
                raise UnverifiedDocumentError('There was a problem verifying the doc for certificate uid=%s',
                                              certificate_metadata.uid)


def find_unsigned_certificates(app_config):
    cert_info = {}
    for filename, (uid,) in glob2.iglob(app_config.unsigned_certs_file_pattern, with_matches=True):
        with open(filename) as cert_file:
            cert_raw = cert_file.read()
            cert_json = json.loads(cert_raw)
            certificate_metadata = CertificateMetadata(app_config,
                                                       uid,
                                                       cert_json['recipient']['givenName'] + ' ' +
                                                       cert_json['recipient']['familyName'],
                                                       cert_json['recipient']['pubkey'])
            cert_info[uid] = certificate_metadata

    return cert_info


def main(app_config):
    certificates_metadata = find_unsigned_certificates(app_config)
    number_of_transactions = len(certificates_metadata)

    start_time = str(time.time())

    if app_config.sign_certificates:
        logging.info('deleting previous generated files')
        #helpers.clear_intermediate_folders()

        logging.info('Signing and hashing %d certificates', number_of_transactions)
        #sign_and_hash_certs(certificates_metadata)
        #helpers.archive_files(app_config.signed_certs_file_pattern, app_config.archived_certs_file_pattern, start_time)

    # calculate transaction costs
    transaction_costs = wallet.get_cost_for_certificate_batch(app_config.dust_threshold, app_config.tx_fees,
                                                              app_config.satoshi_per_byte, number_of_transactions,
                                                              app_config.transfer_from_storage_address)
    logging.info('Total cost will be %d satoshis', transaction_costs.total)

    # ensure there is enough in our wallet at the storage/issuing address
    wt = Wallet(connectors.create_wallet_connector(app_config))
    broadcast_function = connectors.create_broadcast_function(app_config)

    issuing_address = app_config.issuing_address
    storage_address = app_config.storage_address
    revocation_address = app_config.revocation_address

    if app_config.transfer_from_storage_address:
        wt.transfer_balance(storage_address, issuing_address, transaction_costs)
    else:
        wt.check_balance(issuing_address, transaction_costs)

    # issue the certificates on the blockchain
    issue_on_blockchain(wt, broadcast_function, issuing_address,
                        revocation_address, certificates_metadata,
                        transaction_costs)


    helpers.archive_files(app_config.sent_txs_file_pattern, app_config.archived_txs_file_pattern, start_time)
    logging.info('Archived sent transactions folder for safe keeping.')


if __name__ == "__main__":
    # Configure logging settings; create console handler and set level to info
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    from issuer.config import CONFIG as app_config

    main(app_config)
