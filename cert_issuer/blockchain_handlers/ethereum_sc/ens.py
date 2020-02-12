from namehash.namehash import namehash
from cert_issuer.blockchain_handlers.ethereum_sc.connectors import EthereumSCServiceProviderConnector
from cert_issuer.errors import UnmatchingENSEntryError
from web3 import Web3, HTTPProvider

from cert_core import Chain

ENS_CONTRACTS = {
    'ethereum_mainnet': {
        'ens_registry': '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e'
        },
    'ethereum_ropsten': {
        'ens_registry': '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e'
        }
    }

class ENSConnector(object):
    def __init__(self, app_config):
        self.app_config = app_config
        self._w3 = Web3(HTTPProvider())

    def get_registry_address(self):
        if self.app_config.chain == Chain.ethereum_ropsten:
            chain = "ethereum_ropsten"
        else:
            chain = "ethereum_mainnet"

        addr = ENS_CONTRACTS[chain]["ens_registry"]
        return self._w3.toChecksumAddress(addr)

    def get_registry_contract(self):
        registry_addr = self.get_registry_address()
        ens_registry = EthereumSCServiceProviderConnector(
                self.app_config,
                contract_address=registry_addr,
                abi_type="ens_registry")
        return ens_registry

    def get_resolver_address(self):
        ens_registry = self.get_registry_contract()
        ens_name = self.app_config.ens_name
        node = self.get_node(ens_name)
        resolver_addr = ens_registry.call("resolver", node)
        return self._w3.toChecksumAddress(resolver_addr)

    def get_resolver_contract(self):
        resolver_addr = self.get_resolver_address()
        ens_resolver = EthereumSCServiceProviderConnector(
                self.app_config,
                contract_address=resolver_addr,
                abi_type="ens_resolver")
        return ens_resolver

    def get_node(self, ens_name):
        return namehash(ens_name)

    def get_addr_by_ens_name(self, ens_name):
        ens_resolver = self.get_resolver_contract()

        ens_name = self.app_config.ens_name
        node = self.get_node(ens_name)

        addr = ens_resolver.call("addr", node)
        return addr
