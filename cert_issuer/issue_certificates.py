import logging
import sys

from cert_schema import Chain
from cert_issuer import helpers
from cert_issuer import signer as signer_helper
from cert_issuer.certificate_handler import CertificateBatchHandler, CertificateV2Handler
from cert_issuer.connectors import BitcoinServiceProviderConnector, EthereumServiceProviderConnector
from cert_issuer.issuer import Issuer
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.transaction_handler import BitcoinTransactionHandler, EthereumTransactionHandler, MockTransactionHandler
from cert_issuer.tx_utils import BitcoinTransactionCostConstants, EthereumTransactionCostConstants

if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this script.\n')
    sys.exit(1)


def issue(app_config, certificate_batch_handler, transaction_handler):
    unsigned_certs_dir = app_config.unsigned_certificates_dir
    signed_certs_dir = app_config.signed_certificates_dir
    blockchain_certificates_dir = app_config.blockchain_certificates_dir
    work_dir = app_config.work_dir

    certificates_metadata = helpers.prepare_issuance_batch(unsigned_certs_dir, signed_certs_dir,
                                                           blockchain_certificates_dir, work_dir)
    num_certificates = len(certificates_metadata)
    if num_certificates < 1:
        logging.warning('No certificates to process')
        return None

    logging.info('Processing %d certificates under work path=%s', num_certificates, work_dir)
    certificate_batch_handler.set_certificates_in_batch(certificates_metadata)

    transaction_handler.ensure_balance()

    issuer = Issuer(
        certificate_batch_handler=certificate_batch_handler,
        transaction_handler=transaction_handler,
        max_retry=app_config.max_retry)
    tx_id = issuer.issue(app_config.bitcoin_chain)

    helpers.copy_output(certificates_metadata)

    logging.info('Your Blockchain Certificates are in %s', blockchain_certificates_dir)
    return tx_id


def main(app_config):
    issuing_address = app_config.issuing_address
    chain = app_config.bitcoin_chain
    secret_manager = signer_helper.initialize_signer(app_config)
    certificate_batch_handler = CertificateBatchHandler(secret_manager=secret_manager,
                                                        certificate_handler=CertificateV2Handler(),
                                                        merkle_tree=MerkleTreeGenerator())
    if chain == Chain.mocknet:
        transaction_handler = MockTransactionHandler()
    #added ethereum chains.
    elif chain == Chain.ethmain or chain == Chain.ethrop or chain == Chain.ethtest:
        cost_constants = EthereumTransactionCostConstants()
        connector = EthereumServiceProviderConnector()
        transaction_handler = EthereumTransactionHandler(connector, cost_constants, secret_manager, issuing_address=issuing_address)
    else:
        cost_constants = BitcoinTransactionCostConstants(app_config.tx_fee, app_config.dust_threshold, app_config.satoshi_per_byte)
        connector = BitcoinServiceProviderConnector(chain, app_config.bitcoind)
        transaction_handler = BitcoinTransactionHandler(connector, cost_constants, secret_manager,
                                                        issuing_address=issuing_address)
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
