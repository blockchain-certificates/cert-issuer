from namehash.namehash import namehash
from cert_issuer.blockchain_handlers.ethereum_sc.connectors import EthereumSCServiceProviderConnector
from cert_issuer.errors import UnmatchingENSEntryError
from web3 import Web3, HTTPProvider

ENS_CONTRACTS = {
    'ethereum_mainnet': {
        'ens_registry': '0x314159265dd8dbb310642f98f50c066173c1259b'
        },
    'ethereum_ropsten': {
        'ens_registry': '0x112234455c3a32fd11230c42e7bccd4a84e02010'
        }
    }

class ENSConnector(object):
    def __init__(self, app_config):
        self.app_config = app_config
        self._w3 = Web3(HTTPProvider())

    def get_registry_address(self):
        addr = ENS_CONTRACTS["ethereum_ropsten"]["ens_registry"]
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


class VerifyENS:
    def __init__(self, app_config):
        self.app_config = app_config
        self.ens = ENSConnector(app_config)

    def verify_ens(self):
        """ Verifies that {ens_name} points to {contract_address} """
        ens_resolver = self.ens.get_resolver_contract()

        ens_name = self.app_config.ens_name
        node = self.ens.get_node(ens_name)

        addr = ens_resolver.call("addr", node)

        if addr != self.app_config.contract_address:
            raise UnmatchingENSEntryError("Contract address set in ENS entry does not match contract address from config")
