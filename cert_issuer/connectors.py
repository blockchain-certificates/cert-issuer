"""
Connectors wrap the details of communicating with different Bitcoin clients and implementations.

"""
import io
import logging

import bitcoin.rpc
import requests
from bitcoin.core import CTransaction
from pycoin.serialize import b2h
from pycoin.services import providers
from pycoin.services.providers import BlockrioProvider, InsightProvider
from pycoin.services.providers import get_default_providers_for_netcode
from pycoin.services.providers import service_provider_methods
from pycoin.tx import Spendable

from cert_issuer.errors import ConnectorError, BroadcastError, UnrecognizedChainError
from cert_issuer.helpers import hexlify
from cert_issuer.helpers import unhexlify

try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode


def try_get(url):
    """throw error if call fails"""
    response = requests.get(url)
    if int(response.status_code) != 200:
        error_message = 'Error! status_code={}, error={}'.format(
            response.status_code, response.json()['error'])
        logging.error(error_message)
        raise ConnectorError(error_message)
    return response


def to_hex(transaction):
    s = io.BytesIO()
    transaction.stream(s)
    tx_as_hex = b2h(s.getvalue())
    return tx_as_hex


class InsightBroadcaster(InsightProvider):
    def __init__(self, base_url, netcode=None):
        InsightProvider.__init__(self, base_url, netcode)
        self.netcode = netcode

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/api/tx/send'
        response = requests.post(broadcast_url, json={'rawtx': hextx})
        if int(response.status_code) == 200:
            tx_id = response.json().get('txid', None)
            return tx_id
        logging.error('Error broadcasting the transaction through the Insight API. Error msg: %s', response.text)
        raise BroadcastError(response.text)


class BlockrBroadcaster(BlockrioProvider):
    def __init__(self, netcode):
        BlockrioProvider.__init__(self, netcode)

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        url = self.url + '/tx/push'
        response = requests.post(url, json={'hex': hextx})
        if int(response.status_code) == 200:
            tx_id = response.json().get('data', None)
            return tx_id
        logging.error('Error broadcasting the transaction through the Blockr.IO API. Error msg: %s', response.text)
        raise BroadcastError(response.text)


class BitcoindConnector(object):
    def __init__(self, netcode):
        self.netcode = netcode

    def broadcast_tx(self, transaction):
        as_hex = transaction.as_hex()
        transaction = CTransaction.deserialize(unhexlify(as_hex))
        tx_id = bitcoin.rpc.Proxy().sendrawtransaction(transaction)
        # reverse endianness for bitcoind
        return hexlify(bytearray(tx_id)[::-1])

    def spendables_for_address(self, address):
        """
        Converts to pycoin Spendable type
        :param address:
        :return: list of Spendables
        """
        unspent_outputs = bitcoin.rpc.Proxy().listunspent(addrs=[address])
        logging.debug('spendables_for_address %s', address)

        spendables = []
        for unspent in unspent_outputs:
            coin_value = unspent.get('amount', 0)
            outpoint = unspent.get('outpoint')
            script = unspent.get('scriptPubKey')
            previous_hash = outpoint.hash
            previous_index = outpoint.n
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables


class ServiceProviderConnector(object):
    def __init__(self, bitcoin_chain, netcode):
        self.bitcoin_chain = bitcoin_chain
        self.netcode = netcode
        self._init_connectors(bitcoin_chain, netcode)

    def spendables_for_address(self, bitcoin_address, netcode):
        for m in service_provider_methods("spendables_for_address", get_default_providers_for_netcode(netcode)):
            try:
                logging.debug('m=%s', m)
                spendables = m(bitcoin_address)
                return spendables
            except Exception as e:
                logging.warning(e)
                pass
        return []

    def get_unspent_outputs(self, address):
        """
        Get unspent outputs at the address
        :param address:
        :return:
        """
        logging.debug('get_unspent_outputs for address=%s, netcode=%s', address, self.netcode)
        spendables = self.spendables_for_address(bitcoin_address=address, netcode=self.netcode)
        if spendables:
            return sorted(spendables, key=lambda x: hash(x.coin_value))
        return None

    def get_balance(self, address):
        """
        Get balance available to spend at the address
        :param address:
        :return:
        """
        spendables = self.get_unspent_outputs(address)
        if not spendables:
            logging.warning('address %s has a balance of 0', address)
            return 0

        balance = sum(s.coin_value for s in spendables)
        return balance

    def broadcast_tx(self, tx):
        """
        Broadcast the transaction through the configured set of providers

        :param tx:
        :return:
        """
        last_exception = None
        for method_provider in service_provider_methods('broadcast_tx',
                                                        get_default_providers_for_netcode(self.netcode)):
            try:
                tx_id = method_provider(tx)
                if tx_id:
                    return tx_id
            except Exception as e:
                logging.warning('Caught exception trying provider %s. Trying another. Exception=%s',
                                str(method_provider), e)
                last_exception = e
        logging.error('Failed broadcasting through all providers')
        logging.error(last_exception, exc_info=True)
        raise last_exception

    def _init_connectors(self, bitcoin_chain, netcode):
        """
        Initialize broadcasting and payment connectors. This allows fallback and confirmation across different chains
        :param wallet_connector_type:
        :return:
        """

        if netcode == 'BTC':
            # configure mainnet providers
            provider_list = providers.providers_for_config_string(PYCOIN_BTC_PROVIDERS, 'BTC')
            self.patch_providers(provider_list, 'BTC')
            providers.set_default_providers_for_netcode('BTC', provider_list)

        elif netcode == 'XTN':
            if bitcoin_chain == 'regtest':
                regtest_list = []
                regtest_list.append(BitcoindConnector('XTN'))
                providers.set_default_providers_for_netcode('XTN', regtest_list)
            else:
                # initialize testnet providers
                provider_list = providers.providers_for_config_string(PYCOIN_XTN_PROVIDERS, 'XTN')
                self.patch_providers(provider_list, 'XTN')
                providers.set_default_providers_for_netcode('XTN', provider_list)

        else:
            logging.error('Unrecognized chain %s', netcode)
            raise UnrecognizedChainError('Unrecognized chain ' + netcode)

    def patch_providers(self, provider_list, netcode):
        blockio_index = -1
        for idx, val in enumerate(provider_list):
            logging.info('idx=%s,val=%s', idx, val)
            if isinstance(val, BlockrioProvider):
                blockio_index = idx
        if blockio_index > -1:
            provider_list[blockio_index] = BlockrBroadcaster(netcode)
        else:
            provider_list.append(BlockrBroadcaster(netcode))
        provider_list.append(InsightBroadcaster('https://insight.bitpay.com/', netcode))


PYCOIN_BTC_PROVIDERS = "blockchain.info blockexplorer.com blockr.io blockcypher.com chain.so"
PYCOIN_XTN_PROVIDERS = "blockexplorer.com chain.so"
