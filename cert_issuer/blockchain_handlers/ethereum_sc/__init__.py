import logging
import os

from cert_core import BlockchainType
from cert_core import Chain, UnknownChainError

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV2Handler
from cert_issuer.blockchain_handlers.ethereum_sc.connectors import EthereumSCServiceProviderConnector
from cert_issuer.blockchain_handlers.ethereum_sc.ens import ENSConnector
from cert_issuer.blockchain_handlers.ethereum_sc.signer import EthereumSCSigner
from cert_issuer.blockchain_handlers.ethereum_sc.transaction_handlers import EthereumSCTransactionHandler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.models import MockTransactionHandler
from cert_issuer.signer import FileSecretManager
from cert_issuer.errors import UnmatchingENSEntryError, MissingArgumentError


class EthereumTransactionCostConstants(object):
    def __init__(self, recommended_gas_price=30000000000, recommended_gas_limit=25000):
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
        signer = EthereumSCSigner(ethereum_chain=app_config.chain)
    elif app_config.chain == Chain.mockchain:
        signer = None
    else:
        raise UnknownChainError(app_config.chain)
    secret_manager = FileSecretManager(signer=signer, path_to_secret=path_to_secret,
                                       safe_mode=app_config.safe_mode, issuing_address=app_config.issuing_address)
    return secret_manager


def instantiate_connector(app_config, cost_constants):
    # if contr_addr is not set explicitly (recommended), get it from ens entry
    ens = ENSConnector(app_config)
    contr_addr = ens.get_addr_by_ens_name(app_config.ens_name)

    if app_config.contract_address is None:
        app_config.contract_address = contr_addr
    else:
        if contr_addr != app_config.contract_address:
            raise UnmatchingENSEntryError("Contract address set in ENS entry does \
                                           not match contract address from config")

    connector = EthereumSCServiceProviderConnector(app_config, contr_addr, cost_constants=cost_constants)
    return connector

def check_necessary_arguments(app_config):
    # required arguments only for smart_contract method
    if app_config.ens_name is None:
        raise MissingArgumentError("Missing argument ens_name, check your config file.")
    if app_config.node_url is None:
        raise MissingArgumentError("Missing argument node_url, check your config file.")

    # required only if revoke is set
    if app_config.revoke is True and app_config.revocation_list_file is None:
        raise MissingArgumentError("Missing argument revocation_list_file, check your config file.")

def instantiate_blockchain_handlers(app_config):
    check_necessary_arguments(app_config)

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
        connector = instantiate_connector(app_config, cost_constants)
        transaction_handler = EthereumSCTransactionHandler(connector, cost_constants, secret_manager,
                                                           issuing_address=issuing_address)

    return certificate_batch_handler, transaction_handler, connector
