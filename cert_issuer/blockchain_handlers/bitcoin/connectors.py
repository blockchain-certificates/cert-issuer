"""
Connectors wrap the details of communicating with different Bitcoin clients and implementations.
"""
import io
import logging
import time
from abc import abstractmethod

import bitcoin.rpc
import requests
from bitcoin.core import CTransaction
from cert_core import Chain
from pycoin.serialize import b2h, b2h_rev, h2b, h2b_rev
from pycoin.services import providers
from pycoin.services.chain_so import ChainSoProvider
from pycoin.services.insight import InsightProvider
from pycoin.services.providers import service_provider_methods
from pycoin.tx.Spendable import Spendable

import cert_issuer.config
from cert_issuer import helpers
from cert_issuer.errors import BroadcastError

try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode

BROADCAST_RETRY_INTERVAL = 30
MAX_BROADCAST_ATTEMPTS = 3


def to_hex(transaction):
    s = io.BytesIO()
    transaction.stream(s)
    tx_as_hex = b2h(s.getvalue())
    return tx_as_hex

class BlockcypherProvider(object):
    """
    Note that this needs an API token
    """

    def __init__(self, base_url, api_token=None):
        self.base_url = base_url
        self.api_token = api_token

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/txs/push'
        if self.api_token:
            broadcast_url += '?token=' + self.api_token
        response = requests.post(broadcast_url, json={'tx': hextx})
        if int(response.status_code) == 201:
            tx_id = response.json().get('tx', None)
            tx_hash = tx_id.get('hash', None)
            return tx_hash
        logging.error('Error broadcasting the transaction through the Blockcypher API. Error msg: %s', response.text)
        raise BroadcastError(response.text)

    def spendables_for_address(self, address):
        """
        Return a list of Spendable objects for the
        given bitcoin address.
        """
        logging.info('trying to get spendables from blockcypher')
        spendables = []
        url_append = '?unspentOnly=true&includeScript=true'
        if self.api_token:
            url_append += '&token=' + self.api_token
        url = self.base_url + '/addrs/' + address + url_append
        response = requests.get(url)
        if int(response.status_code) == 200:
            for txn in response.json().get('txrefs', []):
                coin_value = txn.get('value')
                script = h2b(txn.get('script'))
                previous_hash = h2b_rev(txn.get('tx_hash'))
                previous_index = txn.get('tx_output_n')
                spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables

class BlockstreamBroadcaster(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/tx'
        response = requests.post(broadcast_url, data=hextx)
        if int(response.status_code) == 200:
            tx_id = response.text
            return tx_id
        logging.error('Error broadcasting the transaction through the Blockstream API. Error msg: %s', response.text)
        raise BroadcastError(response.text)

class BitcoindConnector(object):
    def __init__(self, netcode):
        self.netcode = netcode

    def broadcast_tx(self, transaction):
        as_hex = transaction.as_hex()
        transaction = CTransaction.deserialize(h2b(as_hex))
        tx_id = bitcoin.rpc.Proxy().sendrawtransaction(transaction)
        # reverse endianness for bitcoind
        return b2h_rev(tx_id)

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
    @abstractmethod
    def get_balance(self, address):
        pass

    def broadcast_tx(self, tx):
        pass


class MockServiceProviderConnector(ServiceProviderConnector):
    def get_balance(self, address):
        pass

    def broadcast_tx(self, tx):
        pass


class BitcoinServiceProviderConnector(ServiceProviderConnector):
    def __init__(self, bitcoin_chain, bitcoind=False):
        self.bitcoin_chain = bitcoin_chain
        self.bitcoind = bitcoind

    def spendables_for_address(self, bitcoin_address):
        for m in service_provider_methods('spendables_for_address',
                                          get_providers_for_chain(self.bitcoin_chain, self.bitcoind)):
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
        logging.debug('get_unspent_outputs for address=%s', address)
        spendables = self.spendables_for_address(bitcoin_address=address)
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
        return BitcoinServiceProviderConnector.broadcast_tx_with_chain(tx, self.bitcoin_chain, self.bitcoind)

    @staticmethod
    def broadcast_tx_with_chain(tx, bitcoin_chain, bitcoind=False):
        """
        Broadcast the transaction through the configured set of providers

        :param tx:
        :param bitcoin_chain:
        :return:
        """
        last_exception = None
        final_tx_id = None

        # Unlike other providers, we want to broadcast to all available apis
        for attempt_number in range(0, MAX_BROADCAST_ATTEMPTS):
            for method_provider in service_provider_methods('broadcast_tx',
                                                            get_providers_for_chain(bitcoin_chain, bitcoind)):
                try:
                    tx_id = method_provider(tx)
                    if tx_id:
                        logging.info('Broadcasting succeeded with method_provider=%s, txid=%s', str(method_provider),
                                     tx_id)
                        if final_tx_id and final_tx_id != tx_id:
                            logging.error(
                                'This should never happen; fail and investigate if it does. Got conflicting tx_ids=%s and %s. Hextx=%s',
                                final_tx_id, tx_id, tx.as_hex())
                            raise Exception('Got conflicting tx_ids.')
                        final_tx_id = tx_id
                except Exception as e:
                    logging.warning('Caught exception trying provider %s. Trying another. Exception=%s',
                                    str(method_provider), e)
                    last_exception = e
            # At least 1 provider succeeded, so return
            if final_tx_id:
                return final_tx_id
            else:
                logging.warning('Broadcasting failed. Waiting before retrying. This is attempt number %d',
                                attempt_number)
                time.sleep(BROADCAST_RETRY_INTERVAL)
        logging.error('Failed broadcasting through all providers')
        logging.error(last_exception, exc_info=True)
        raise BroadcastError(last_exception)


# configure api tokens
config = cert_issuer.config.CONFIG
blockcypher_token = None if config is None else config.blockcypher_api_token

PYCOIN_BTC_PROVIDERS = "blockchain.info chain.so"  # blockcypher.com
PYCOIN_XTN_PROVIDERS = ""  # chain.so

# initialize connectors
connectors = {}

# configure mainnet providers
provider_list = providers.providers_for_config_string(PYCOIN_BTC_PROVIDERS,
                                                      helpers.to_pycoin_chain(Chain.bitcoin_mainnet))
provider_list.append(BlockcypherProvider('https://api.blockcypher.com/v1/btc/main', blockcypher_token))
provider_list.append(InsightProvider(netcode=helpers.to_pycoin_chain(Chain.bitcoin_mainnet)))
provider_list.append(ChainSoProvider(netcode=helpers.to_pycoin_chain(Chain.bitcoin_mainnet)))
provider_list.append(BlockstreamBroadcaster('https://blockstream.info/api'))
connectors[Chain.bitcoin_mainnet] = provider_list

# configure testnet providers
xtn_provider_list = providers.providers_for_config_string(PYCOIN_XTN_PROVIDERS,
                                                          helpers.to_pycoin_chain(Chain.bitcoin_testnet))
xtn_provider_list.append(ChainSoProvider(netcode=helpers.to_pycoin_chain(Chain.bitcoin_testnet)))
xtn_provider_list.append(BlockcypherProvider('https://api.blockcypher.com/v1/btc/test3', blockcypher_token))
xtn_provider_list.append(BlockstreamBroadcaster('https://blockstream.info/testnet/api'))
connectors[Chain.bitcoin_testnet] = xtn_provider_list


def get_providers_for_chain(chain, bitcoind=False):
    if bitcoind:
        return [BitcoindConnector(helpers.to_pycoin_chain(chain))]
    else:
        return connectors[chain]
