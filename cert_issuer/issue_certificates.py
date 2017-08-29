import logging
import os
import shutil
import sys

from cert_issuer import helpers
from cert_issuer import signer as signer_helper
from cert_issuer.certificate_handler import CertificateBatchHandler
from cert_issuer.connectors import ServiceProviderConnector
from cert_issuer.issuer import Issuer
from cert_issuer.transaction_handler import BitcoinTransactionHandler
from cert_issuer.tx_utils import TransactionCostConstants

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def issue(app_config, certificate_batch_handler, transaction_handler):
    unsigned_certs_dir = app_config.unsigned_certificates_dir
    signed_certs_dir = app_config.signed_certificates_dir
    blockchain_certificates_dir = app_config.blockchain_certificates_dir
    work_dir = app_config.work_dir

    certificates, batch_metadata = helpers.prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir,
                                                                  blockchain_certificates_dir, work_dir)
    num_certificates = len(certificates)
    if num_certificates < 1:
        logging.warning('No certificates to process')
        return None

    logging.info('Processing %d certificates under work path=%s', num_certificates, work_dir)
    certificate_batch_handler.certificates_to_issue = certificates

    transaction_handler.ensure_balance()

    issuer = Issuer(
        certificate_batch_handler=certificate_batch_handler,
        transaction_handler=transaction_handler,
        max_retry=app_config.max_retry)
    tx_id = issuer.issue_certificates()

    blockcerts_tmp_dir = os.path.join(work_dir, helpers.BLOCKCHAIN_CERTIFICATES_DIR)
    if not os.path.exists(blockchain_certificates_dir):
        os.makedirs(blockchain_certificates_dir)
    for item in os.listdir(blockcerts_tmp_dir):
        s = os.path.join(blockcerts_tmp_dir, item)
        d = os.path.join(blockchain_certificates_dir, item)
        shutil.copy2(s, d)

    logging.info('Your Blockchain Certificates are in %s', blockchain_certificates_dir)
    return tx_id


def main(app_config):
    issuing_address = app_config.issuing_address
    connector = ServiceProviderConnector(app_config.bitcoin_chain)
    cost_constants = TransactionCostConstants(app_config.tx_fee, app_config.dust_threshold, app_config.satoshi_per_byte)

    secret_manager = signer_helper.initialize_signer(app_config)
    transaction_handler = BitcoinTransactionHandler(connector, cost_constants, secret_manager,
                                                    issuing_address=issuing_address)
    certificate_batch_handler = CertificateBatchHandler(secret_manager=secret_manager)
    return issue(app_config, certificate_batch_handler, transaction_handler)


if __name__ == '__main__':
    from cert_issuer import config

    try:
        parsed_config = config.get_config()
        tx_id = main(parsed_config)
        if tx_id:
            logging.info('Transaction id is %s', tx_id)
        else:
            logging.error('Certificate issuing failed')
            exit(1)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        exit(1)
