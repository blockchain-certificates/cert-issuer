"""
Base class for building blockchain transactions to issue Blockchain Certificates.
"""
import logging

from cert_issuer.errors import BroadcastError
from cert_issuer.helpers import unhexlify

MAX_TX_RETRIES = 5


class Issuer:
    def __init__(self, certificate_batch_handler, transaction_handler, max_retry=MAX_TX_RETRIES):
        self.certificate_batch_handler = certificate_batch_handler
        self.transaction_handler = transaction_handler
        self.max_retry = max_retry

    def issue(self):
        """
        Issue the certificates on the blockchain
        :return:
        """

        op_return = self.certificate_batch_handler.prepare_batch()
        op_return_bytes = unhexlify(op_return)

        for attempt_number in range(0, self.max_retry):
            try:
                txid = self.transaction_handler.issue_transaction(op_return_bytes)
                self.certificate_batch_handler.finish_batch(txid)
                logging.info('Broadcast transaction with txid %s', txid)
                return txid
            except BroadcastError:
                logging.warning(
                    'Failed broadcast reattempts. Trying to recreate transaction. This is attempt number %d',
                    attempt_number)
        logging.error('All attempts to broadcast failed. Try rerunning issuer.')
        raise BroadcastError('All attempts to broadcast failed. Try rerunning issuer.')
