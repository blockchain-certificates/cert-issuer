import logging
import os

from cert_core import UnknownChainError

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV3Handler, CertificateBatchWebHandler, CertificateWebV3Handler
from cert_issuer.blockchain_handlers.ethereum.connectors import EthereumServiceProviderConnector
from cert_issuer.blockchain_handlers.ethereum.signer import EthereumSigner
from cert_issuer.blockchain_handlers.ethereum.transaction_handlers import EthereumTransactionHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.models import MockTransactionHandler
from cert_issuer.signer import FileSecretManager

ONE_BILLION = 1000000000


class EthereumTransactionCostConstants(object):
    def __init__(self, max_priority_fee_per_gas, recommended_gas_price, recommended_gas_limit):
        self.max_priority_fee_per_gas = max_priority_fee_per_gas
        self.recommended_gas_price = recommended_gas_price
        self.recommended_gas_limit = recommended_gas_limit
        logging.info('Set cost constants to recommended_gas_price=%f Gwei, recommended_gas_limit=%d gas',
            self.recommended_gas_price / ONE_BILLION, self.recommended_gas_limit)
        if self.max_priority_fee_per_gas:
            logging.info('and max_priority_fee_per_gas=%f Gwei', self.max_priority_fee_per_gas / ONE_BILLION)

    """
    The below methods currently only use the supplied gasprice/limit.
    These values can also be better estimated via a call to the Ethereum blockchain.
    """

    def get_recommended_max_cost(self):
        return self.recommended_gas_price * self.recommended_gas_limit

    def get_max_priority_fee_per_gas(self):
        return self.max_priority_fee_per_gas

    def get_gas_price(self):
        return self.recommended_gas_price

    def get_gas_limit(self):
        return self.recommended_gas_limit


def initialize_signer(app_config):
    path_to_secret = os.path.join(app_config.usb_name, app_config.key_file)

    if app_config.chain.is_ethereum_type():
        signer = EthereumSigner(ethereum_chain=app_config.chain)
    elif app_config.is_mock_type():
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

    certificate_batch_handler = (CertificateBatchHandler if file_mode else CertificateBatchWebHandler)(
        secret_manager=secret_manager,
        certificate_handler=(CertificateV3Handler if file_mode else CertificateWebV3Handler)(app_config),
        merkle_tree=MerkleTreeGenerator(),
        config=app_config
    )

    if chain.is_mock_type():
        transaction_handler = MockTransactionHandler()
    # ethereum chains
    elif chain.is_ethereum_type():
        nonce = app_config.nonce
        connector = EthereumServiceProviderConnector(chain, app_config)

        if app_config.gas_price_dynamic:
            gas_price = connector.gas_price()
        else:
            gas_price = app_config.gas_price

        cost_constants = EthereumTransactionCostConstants(app_config.max_priority_fee_per_gas,
                                                          gas_price, app_config.gas_limit)

        transaction_handler = EthereumTransactionHandler(connector, nonce, cost_constants, secret_manager,
                                                         issuing_address=issuing_address)

    return certificate_batch_handler, transaction_handler, connector
