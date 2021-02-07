import logging
import os

from cert_core import BlockchainType
from cert_core import Chain, UnknownChainError

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV2Handler
from cert_issuer.blockchain_handlers.ethereum.connectors import EthereumServiceProviderConnector
from cert_issuer.blockchain_handlers.ethereum.signer import EthereumSigner
from cert_issuer.blockchain_handlers.ethereum.transaction_handlers import EthereumTransactionHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.models import MockTransactionHandler
from cert_issuer.signer import FileSecretManager


class EthereumTransactionCostConstants(object):
    def __init__(self, recommended_gas_price=20000000000, recommended_gas_limit=25000):
        self.recommended_gas_price = recommended_gas_price
        self.recommended_gas_limit = recommended_gas_limit
        logging.info('Set cost constants to recommended_gas_price=%f, recommended_gas_limit=%f',
                     self.recommended_gas_price, self.recommended_gas_limit)

    """
    The below methods currently only use the supplied gasprice/limit.
    These values can also be better estimated via a call to the Ethereum blockchain.
    """

    def get_recommended_max_cost(self):
        return self.recommended_gas_price * self.recommended_gas_limit

    def get_gas_price(self):
        return self.recommended_gas_price

    def get_gas_limit(self):
        return self.recommended_gas_limit


def initialize_signer(app_config):
    path_to_secret = os.path.join(app_config.usb_name, app_config.key_file)

    if app_config.chain.blockchain_type == BlockchainType.ethereum:
        signer = EthereumSigner(ethereum_chain=app_config.chain)
    elif app_config.chain == Chain.mockchain:
        signer = None
    else:
        raise UnknownChainError(app_config.chain)
    secret_manager = FileSecretManager(signer=signer, path_to_secret=path_to_secret,
                                       safe_mode=app_config.safe_mode, issuing_address=app_config.issuing_address)
    return secret_manager


def instantiate_blockchain_handlers(app_config):
    issuing_address = app_config.issuing_address
    chain = app_config.chain
    secret_manager = initialize_signer(app_config)
    certificate_batch_handler = CertificateBatchHandler(secret_manager=secret_manager,
                                                        certificate_handler=CertificateV2Handler(),
                                                        merkle_tree=MerkleTreeGenerator())
    if chain == Chain.mockchain:
        transaction_handler = MockTransactionHandler()
    # ethereum chains
    elif chain == Chain.ethereum_mainnet or chain == Chain.ethereum_ropsten:
        cost_constants = EthereumTransactionCostConstants(app_config.gas_price, app_config.gas_limit)
        connector = EthereumServiceProviderConnector(chain, app_config)
        transaction_handler = EthereumTransactionHandler(connector, cost_constants, secret_manager,
                                                         issuing_address=issuing_address)

    return certificate_batch_handler, transaction_handler, connector
