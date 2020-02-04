"""
Base class for building blockchain transactions to issue Blockchain Certificates.
"""
import logging
import json

from pycoin.serialize import h2b

from cert_issuer.errors import BroadcastError

MAX_TX_RETRIES = 5


def ensure_string(value):
    if isinstance(value, str):
        return value
    return value.decode('utf-8')


def get_revocation_hashes(app_config):
    revocation_list_file = app_config.revocation_list_file
    with open(revocation_list_file, "r") as f:
        data = f.read()
    revocations = json.loads(data)
    hashes = revocations["hashes_to_be_revoked"]
    return hashes


def update_revocations_list(app_config, revoked_hashes, remaining_hashes):
    revocation_list_file = app_config.revocation_list_file
    with open(revocation_list_file, "r") as f:
        data = f.read()
    revocations = json.loads(data)

    revocations["hashes_to_be_revoked"] = remaining_hashes
    revocations["revoked_assertions"] += revoked_hashes

    with open(revocation_list_file, "w+") as f:
        data = json.dump(revocations, f, indent=4)


class Revoker:
    def __init__(self, transaction_handler, max_retry=MAX_TX_RETRIES):
        self.transaction_handler = transaction_handler
        self.max_retry = max_retry

    def revoke(self, app_config):
        """
        Issue the certificates on the blockchain
        :return:
        """

        hashes = get_revocation_hashes(app_config)

        revoked_hashes = []
        tx_ids = []

        if hashes == []:
            logging.info('No hashes to revoke. Check your revocation_list_file if you meant to revoke hashes.')
            return None

        for hash in hashes:
            # ensure balance before every transaction
            self.transaction_handler.ensure_balance()

            # transform to hex
            blockchain_bytes = h2b(ensure_string(hash))

            try:
                txid = self.transaction_handler.issue_transaction("revoke_hash", blockchain_bytes, app_config)
                logging.info('Broadcast transaction with txid %s', txid)

                tx_ids.append(txid)

                # convert to sets for easy difference operation, back to list
                revoked_hashes.append(hash)
                remaining_hashes = sorted(set(hashes)-set(revoked_hashes))
                update_revocations_list(app_config, revoked_hashes, remaining_hashes)
            except BroadcastError:
                logging.warning('Failed broadcast of transaction.')

        return tx_ids
