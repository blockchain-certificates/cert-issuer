import logging
import os

from cert_core import UnknownChainError

from cert_issuer.blockchain_handlers.bitcoin.connectors import BitcoinServiceProviderConnector, MockServiceProviderConnector
from cert_issuer.blockchain_handlers.bitcoin.signer import BitcoinSigner
from cert_issuer.blockchain_handlers.bitcoin.transaction_handlers import BitcoinTransactionHandler
from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV3Handler, CertificateBatchWebHandler, CertificateWebV3Handler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.models import MockTransactionHandler
from cert_issuer.signer import FileSecretManager

COIN = 100000000  # satoshis in 1 btc


class BitcoinTransactionCostConstants(object):
    def __init__(self, recommended_tx_fee=0.0006, min_per_output=0.0000275, satoshi_per_byte=250):
        self.recommended_tx_fee = recommended_tx_fee
        self.min_per_output = min_per_output
        self.satoshi_per_byte = satoshi_per_byte
        logging.info('Set cost constants to recommended_tx_fee=%f,min_per_output=%f,satoshi_per_byte=%d',
                     self.recommended_tx_fee, self.min_per_output, self.satoshi_per_byte)

    def get_minimum_output_coin(self):
        return self.min_per_output * COIN

    def get_recommended_fee_coin(self):
        return self.recommended_tx_fee * COIN


def initialize_signer(app_config):
    path_to_secret = os.path.join(app_config.usb_name, app_config.key_file)

    if app_config.chain.is_bitcoin_type():
        signer = BitcoinSigner(bitcoin_chain=app_config.chain)
    elif app_config.chain.is_mock_type():
        signer = None
    else:
        raise UnknownChainError(app_config.chain)
    secret_manager = FileSecretManager(signer=signer, path_to_secret=path_to_secret,
                                       safe_mode=app_config.safe_mode, issuing_address=app_config.issuing_address)
    return secret_manager

def instantiate_blockchain_handlers(app_config, file_mode=True):
    issuing_address = app_config.issuing_address
    chain = app_config.chain
    secret_manager = initialize_signer(app_config)

    if file_mode:
        certificate_batch_handler = CertificateBatchHandler(secret_manager=secret_manager,
                                                            certificate_handler=CertificateV3Handler(app_config),
                                                            merkle_tree=MerkleTreeGenerator(),
                                                            config=app_config)
    else:
        certificate_batch_handler = CertificateBatchWebHandler(secret_manager=secret_manager,
                                                               certificate_handler=CertificateWebV3Handler(app_config),
                                                               merkle_tree=MerkleTreeGenerator(),
                                                               config=app_config)
    if chain.is_mock_type():
        transaction_handler = MockTransactionHandler()
        connector = MockServiceProviderConnector()
    else:
        cost_constants = BitcoinTransactionCostConstants(app_config.tx_fee, app_config.dust_threshold,
                                                         app_config.satoshi_per_byte)
        connector = BitcoinServiceProviderConnector(chain, app_config.bitcoind)
        transaction_handler = BitcoinTransactionHandler(connector, cost_constants, secret_manager,
                                                        issuing_address=issuing_address)

    return certificate_batch_handler, transaction_handler, connector
