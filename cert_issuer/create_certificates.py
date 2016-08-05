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
import time

import bitcoin
import glob2
import hashlib
from bitcoin.core import CScript, CMutableTransaction, CMutableTxOut, CTxIn
from bitcoin.core.script import OP_RETURN
from bitcoin.signmessage import BitcoinMessage, SignMessage
from bitcoin.signmessage import VerifyMessage
from bitcoin.wallet import CBitcoinAddress
from bitcoin.wallet import CBitcoinSecret
from cert_issuer import connectors
from cert_issuer import helpers
from cert_issuer import wallet as wallet_helper
from cert_issuer.errors import UnverifiedDocumentError, UnverifiedSignatureError
from cert_issuer.helpers import hexlify
from cert_issuer.helpers import internet_off_for_scope
from cert_issuer.models import CertificateMetadata
from cert_issuer.wallet import Wallet
from pycoin.encoding import wif_to_secret_exponent
from pycoin.tx import Tx, TxOut
from pycoin.tx.pay_to import build_hash160_lookup

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def do_sign(certificate, secret_key):
    """Signs the certificate.
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
        error_message = 'There was a problem with the signature for certificate uid={}'.format(
            signed_cert_json['assertion']['uid'])
        raise UnverifiedSignatureError(error_message)


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
                        certificates_to_issue, fees, transfer_from_storage_address, allowable_wif_prefixes):
    tail = -1
    for uid, certificate_metadata in certificates_to_issue.items():
        if transfer_from_storage_address:
            current_tail = tail
            tail -= 1
        else:
            current_tail = -1
        last_input = _build_certificate_transactions(wallet, issuing_address, revocation_address,
                                                     certificate_metadata, fees, current_tail)
        # sign transaction
        sign_tx(certificate_metadata, last_input, allowable_wif_prefixes)

        # verify
        verify(certificate_metadata, issuing_address)

        # broadcast via configurable broadcast_function
        send_tx(broadcast_function, certificate_metadata)


def _build_certificate_transactions(wallet, issuing_address, revocation_address, certificate_metadata, fees, tail):
    """Make transactions for the certificates.
    """
    logging.info('Creating tx of certificate for recipient uid: %s ...',
                 certificate_metadata.uid)

    with open(certificate_metadata.certificate_hash_file_name, 'rb') as in_file:
        # this is the recipient-specific hash that will be recorded on the
        # blockchain
        hashed_certificate = in_file.read()
        cert_out = CMutableTxOut(0, CScript([OP_RETURN, hashed_certificate]))

        # send a transaction to the recipient's public key, and to a revocation
        # address
        txouts = create_recipient_outputs(
            certificate_metadata.pubkey, revocation_address, fees.min_per_output)

        # define transaction inputs
        unspent_outputs = wallet.get_unspent_outputs(issuing_address)
        last_input = unspent_outputs[tail]

        txins = [CTxIn(last_input.outpoint)]
        value_in = last_input.amount

        # very important! If we don't send the excess change back to ourselves,
        # some lucky miner gets it!
        amount = value_in - fees.cost_per_transaction
        if amount > 0:
            change_out = create_transaction_output(issuing_address, amount)
            txouts = txouts + [change_out]

        txouts = txouts + [cert_out]
        tx = CMutableTransaction(txins, txouts)

        # this is the transaction for a recipient, unsigned
        hextx = hexlify(tx.serialize())
        with open(certificate_metadata.unsigned_tx_file_name, 'wb') as out_file:
            out_file.write(bytes(hextx, 'utf-8'))

        logging.info(
            'Created unsigned tx for recipient; last_input=%s', last_input)
        return last_input


def create_recipient_outputs(recipient_address, revocation_address, transaction_fee):
    """Create a pair of outputs: one to the recipient, and one to the revocation address."""
    recipient_out = create_transaction_output(
        recipient_address, transaction_fee)
    revoke_out = create_transaction_output(revocation_address, transaction_fee)
    recipient_outs = [recipient_out] + [revoke_out]
    return recipient_outs


def create_transaction_output(address, transaction_fee):
    """Create a transaction output"""
    addr = CBitcoinAddress(address)
    tx_out = CMutableTxOut(transaction_fee, addr.to_scriptPubKey())
    return tx_out


@internet_off_for_scope
def sign_tx(certificate_metadata, last_input, allowable_wif_prefixes=None):
    """sign the transaction with private key"""
    with open(certificate_metadata.unsigned_tx_file_name, 'rb') as in_file:
        hextx = str(in_file.read(), 'utf-8')

        logging.info(
            'Signing tx with private key for recipient id: %s ...', certificate_metadata.uid)

        tx = Tx.from_hex(hextx)
        if allowable_wif_prefixes:
            wif = wif_to_secret_exponent(
                helpers.import_key(), allowable_wif_prefixes)
        else:
            wif = wif_to_secret_exponent(helpers.import_key())

        lookup = build_hash160_lookup([wif])

        tx.set_unspents(
            [TxOut(coin_value=last_input.amount, script=last_input.script_pub_key)])

        signed_tx = tx.sign(lookup)
        signed_hextx = signed_tx.as_hex()
        with open(certificate_metadata.unsent_tx_file_name, 'wb') as out_file:
            out_file.write(bytes(signed_hextx, 'utf-8'))

    logging.info('Finished signing transaction for certificate uid=%s',
                 certificate_metadata.uid)


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
            logging.warning(
                'could not broadcast transaction but you can manually do it! hextx=%s', hextx)


def verify(certificate_metadata, issuing_address):
    logging.info('verifying certificate with uid=%s:',
                 certificate_metadata.uid)
    with open(certificate_metadata.signed_certificate_file_name) as in_file:
        do_verify_signature(issuing_address, in_file.read())
        logging.info('verified signature')
        verify_doc(certificate_metadata)
        logging.info('verified OP_RETURN')


def verify_doc(certificate_metadata):
    with open(certificate_metadata.signed_certificate_file_name, 'rb') as in_file:
        hashed_cert = hashlib.sha256(in_file.read()).hexdigest()
        unsent_tx_file_name = certificate_metadata.unsent_tx_file_name

        with open(unsent_tx_file_name) as unsent_tx_file:
            op_return_hash = unsent_tx_file.read()[-72:-8]
            result = (hashed_cert == op_return_hash)
            if not result:
                error_message = 'There was a problem verifying the doc for certificate uid={}'.format(
                    certificate_metadata.uid)
                raise UnverifiedDocumentError(error_message)


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
    # find certificates to process
    certificates_metadata = find_signed_certificates(app_config)
    if not certificates_metadata:
        logging.info('No certificates to process')
        exit(0)

    logging.info('Processing %d certificates', len(certificates_metadata))

    allowable_wif_prefixes = app_config.allowable_wif_prefixes
    wallet = Wallet(connectors.create_wallet_connector(app_config))
    broadcast_function = connectors.create_broadcast_function(app_config)

    # get issuing and revocation addresses from config
    issuing_address = app_config.issuing_address
    revocation_address = app_config.revocation_address

    start_time = str(time.time())

    # TODO: fix which folders
    #logging.info('Deleting previous generated files')
    #helpers.clear_intermediate_folders(app_config)

    logging.info('Hashing signed certificates.')
    hash_certs(certificates_metadata)

    logging.info('Archiving signed certificates.')
    helpers.archive_files(app_config.signed_certs_file_pattern,
                          app_config.archived_certs_file_pattern, start_time)

    # calculate transaction costs
    transaction_costs = wallet_helper.get_cost_for_certificate_batch(app_config.dust_threshold, app_config.tx_fee,
                                                                     app_config.satoshi_per_byte,
                                                                     len(certificates_metadata),
                                                                     app_config.transfer_from_storage_address)
    logging.info('Total cost will be %d satoshis', transaction_costs.total)

    # ensure there is enough in our wallet at the storage/issuing address, transferring from the storage address
    # if configured (advanced option)
    if app_config.transfer_from_storage_address:
        storage_address = app_config.storage_address
        wallet.transfer_balance(
            storage_address, issuing_address, transaction_costs)

    logging.info('Checking there is enough balance in the wallet.')
    wallet.check_balance(issuing_address, transaction_costs)

    # issue the certificates on the blockchain
    logging.info('Issuing the certificates on the blockchain')
    issue_on_blockchain(wallet, broadcast_function, issuing_address,
                        revocation_address, certificates_metadata,
                        transaction_costs, issue_on_blockchain, allowable_wif_prefixes)

    # archive
    logging.info('Archived sent transactions folder for safe keeping.')
    helpers.archive_files(app_config.sent_txs_file_pattern,
                          app_config.archived_txs_file_pattern, start_time)

    logging.info('Done!')
