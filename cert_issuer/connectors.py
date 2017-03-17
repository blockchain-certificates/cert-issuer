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
from pycoin.services.providers import service_provider_methods
from pycoin.tx import Spendable

from cert_issuer.errors import ConnectorError, BroadcastError
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


class BlockExplorerBroadcaster(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/tx/send'
        response = requests.post(broadcast_url, json={'rawtx': hextx})
        if int(response.status_code) == 200:
            tx_id = response.json().get('txid', None)
            return tx_id
        logging.error('Error broadcasting the transaction through the BlockExplorer API. Error msg: %s', response.text)
        raise BroadcastError(response.text)


class BlockcypherBroadcaster(object):
    """
    Note that this needs an API token
    """

    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        broadcast_url = self.base_url + '/txs/push?token=' + self.api_token
        response = requests.post(broadcast_url, json={'tx': hextx})
        if int(response.status_code) == 200:
            tx_id = response.json().get('txid', None)
            return tx_id
        logging.error('Error broadcasting the transaction through the Blockcypher API. Error msg: %s', response.text)
        raise BroadcastError(response.text)


class BlockrIOBroadcaster(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def broadcast_tx(self, tx):
        hextx = to_hex(tx)
        url = self.base_url + '/tx/push'
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

    def spendables_for_address(self, bitcoin_address):
        for m in service_provider_methods('spendables_for_address', get_providers_for_netcode(self.netcode,
                                                                                              self.bitcoin_chain)):
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
        logging.debug('get_unspent_outputs for address=%s, netcode=%s', address)
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

        return ServiceProviderConnector.broadcast_tx_with_netcode(tx, self.netcode, self.bitcoin_chain)

    @staticmethod
    def broadcast_tx_with_netcode(tx, netcode, bitcoin_chain=None):
        """
        Broadcast the transaction through the configured set of providers

        :param tx:
        :param netcode:
        :return:
        """
        last_exception = None
        final_tx_id = None
        # Unlike other providers, we want to broadcast to all available apis
        for method_provider in service_provider_methods('broadcast_tx',
                                                        get_providers_for_netcode(netcode, bitcoin_chain)):
            try:
                tx_id = method_provider(tx)
                if tx_id:
                    final_tx_id = tx_id
            except Exception as e:
                logging.warning('Caught exception trying provider %s. Trying another. Exception=%s',
                                str(method_provider), e)
                last_exception = e
        if final_tx_id:
            return final_tx_id
        logging.error('Failed broadcasting through all providers')
        logging.error(last_exception, exc_info=True)
        raise last_exception


PYCOIN_BTC_PROVIDERS = "blockchain.info blockexplorer.com blockr.io blockcypher.com chain.so"
PYCOIN_XTN_PROVIDERS = "blockexplorer.com chain.so"

# initialize connectors
connectors = {}

# configure mainnet providers
provider_list = providers.providers_for_config_string(PYCOIN_BTC_PROVIDERS, 'BTC')
provider_list.append(BlockrIOBroadcaster('https://btc.blockr.io/api/v1'))
provider_list.append(BlockExplorerBroadcaster('https://blockexplorer.com/api'))
connectors['BTC'] = provider_list

# configure testnet providers
xtn_provider_list = providers.providers_for_config_string(PYCOIN_XTN_PROVIDERS, 'XTN')
xtn_provider_list.append(BlockrIOBroadcaster('https://tbtc.blockr.io/api/v1'))
xtn_provider_list.append(BlockExplorerBroadcaster('https://testnet.blockexplorer.com/api'))
connectors['XTN'] = xtn_provider_list

# workaround for regtest
connectors['REG'] = [BitcoindConnector('XTN')]


def get_providers_for_netcode(netcode, bitcoin_chain):
    if bitcoin_chain and bitcoin_chain == 'regtest' and netcode == 'XTN':
        return connectors['REG']
    return connectors[netcode]


# Additional providers to add:
# - chain.so
#   - API docs https://chain.so/api#send-transaction
#   - Broadcast: https://chain.so/api/v2/send_tx/{NETWORK} -> response tx_hex={}
# - blocktrail
#   - https://api.blocktrail.com/v1/tBTC (and BTC)
# - blockcypher (needs API tokens)
#   - provider_list.append(BlockcypherBroadcaster('https://api.blockcypher.com/v1/btc/main'))
#   - xtn_provider_list.append(BlockcypherBroadcaster('https://api.blockcypher.com/v1/btc/test3'))
