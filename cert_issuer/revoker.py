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


def remove_from_revocations_list(app_config, hash):
    revocation_list_file = app_config.revocation_list_file
    with open(revocation_list_file, "r") as f:
        data = f.read()
    revocations = json.loads(data)

    revocations["hashes_to_be_revoked"].remove(hash)

    with open(revocation_list_file, "w+") as f:
        data = json.dump(revocations, f, indent=4)


class Revoker:
    def __init__(self, transaction_handler, max_retry=MAX_TX_RETRIES):
        self.transaction_handler = transaction_handler
        self.max_retry = max_retry

    def revoke(self, app_config):
        """
        Revoke certificates or batches on the blockchain listed in revocation_list_file.
        Multiple transactions will be executed.
        :return:
        """

        hashes = get_revocation_hashes(app_config)

        tx_ids = []

        if hashes == []:
            logging.info('No hashes to revoke. Check your revocation_list_file if you meant to revoke hashes.')
            return None
        else:
            logging.info('Revoking the following hashes: %s', hashes)

        while len(hashes) > 0:
            hash = hashes.pop()
            # ensure balance before every transaction
            self.transaction_handler.ensure_balance()

            # transform to hex
            blockchain_bytes = h2b(ensure_string(hash))

            try:
                txid = self.transaction_handler.revoke_transaction(blockchain_bytes, app_config)
                logging.info('Broadcast revocation of hash %s in tx with txid %s', hash, txid)

                tx_ids.append(txid)

                remove_from_revocations_list(app_config, hash)
            except BroadcastError:
                logging.warning('Failed broadcast of transaction.')

        return tx_ids
