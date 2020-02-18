from ens import ENS
import json
from cert_issuer.blockchain_handlers.ethereum_sc.connectors import EthereumSCServiceProviderConnector
from web3 import Web3, HTTPProvider

from cert_core import Chain

class ENSConnector(object):
    def __init__(self, app_config):
        self.app_config = app_config
        self._w3 = Web3(HTTPProvider())

    def get_registry_address(self):
        if self.app_config.chain == Chain.ethereum_ropsten:
            addr = self.app_config.ens_registry_ropsten
        else:
            addr = self.app_config.ens_registry_mainnet

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
        return ENS.namehash(ens_name)

    def get_abi(self):
        ens_resolver = self.get_resolver_contract()

        node = self.get_node(self.app_config.ens_name)

        abi = ens_resolver.call("ABI", node, 1) # 1 for content type json
        return json.loads(abi[1])

    def get_addr(self):
        ens_resolver = self.get_resolver_contract()

        node = self.get_node(self.app_config.ens_name)

        addr = ens_resolver.call("addr", node)
        return addr
