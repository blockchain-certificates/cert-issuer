import logging
import os

from cert_core import BlockchainType
from cert_core import Chain, UnknownChainError

from cert_issuer.certificate_handlers import CertificateBatchHandler, CertificateV2Handler
from cert_issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_issuer.models import MockTransactionHandler
from cert_issuer.signer import FileSecretManager

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
    # ethereum chains with transaction_handler = app_config --> when calling transaction_handler later it can independently instantiate w3 objects, etc. (app_config contains sufficient data)
    elif chain == Chain.ethereum_mainnet or chain == Chain.ethereum_ropsten:
        transaction_handler = app_config

    return certificate_batch_handler, transaction_handler, connector
